import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from database import get_db
import models, schemas, auth as auth_utils
from ml_service import classify_complaint, get_resolution_advice
from email_service import send_submission_email

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_MB   = 5


def _generate_id(db: Session) -> str:
    count = db.query(models.Complaint).count()
    return f"CMP{str(count + 1).zfill(5)}"


def _save_image(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG, PNG, WEBP or GIF images are allowed.")
    contents = file.file.read()
    if len(contents) > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"Image must be under {MAX_SIZE_MB}MB.")
    ext      = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as f:
        f.write(contents)
    return filename


@router.post("/", response_model=schemas.ComplaintOut, status_code=201)
def submit_complaint(
    complaint_text: str = Form(...),
    channel: Optional[str] = Form("Web Form"),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if not complaint_text.strip():
        raise HTTPException(status_code=400, detail="Complaint text cannot be empty")
    if len(complaint_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Please describe your complaint in at least 10 characters.")

    category, priority = classify_complaint(complaint_text)
    resolution_note    = get_resolution_advice(category, priority, complaint_text)

    image_path = None
    if image and image.filename:
        image_path = _save_image(image)

    assignment = db.query(models.CategoryAssignment).filter(
        models.CategoryAssignment.category == category
    ).first()
    assigned_to_id = assignment.assigned_user_id if assignment else None

    complaint = models.Complaint(
        complaint_id=_generate_id(db),
        user_id=current_user.id,
        complaint_text=complaint_text,
        category=category,
        priority=priority,
        status="Open",
        resolution_note=resolution_note,
        channel=channel or "Web Form",
        sla_breached=False,
        image_path=image_path,
        assigned_to_id=assigned_to_id,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    db.add(models.ComplaintStatusHistory(
        complaint_id=complaint.complaint_id,
        status="Open",
        changed_by_name=current_user.name,
        changed_by_role=current_user.role,
        note="Complaint submitted by customer.",
    ))
    db.commit()

    send_submission_email(
        to_email=current_user.email,
        user_name=current_user.name,
        complaint_id=complaint.complaint_id,
        category=complaint.category,
        priority=complaint.priority,
        complaint_text=complaint.complaint_text,
        resolution_note=complaint.resolution_note or "",
    )

    return complaint


@router.get("/my", response_model=schemas.ComplaintListOut)
def get_my_complaints(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    query = db.query(models.Complaint).filter(models.Complaint.user_id == current_user.id)

    if search:
        query = query.filter(models.Complaint.complaint_text.ilike(f"%{search}%"))
    if status:
        query = query.filter(models.Complaint.status == status)
    if date_from:
        try:
            df = datetime.strptime(date_from, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            query = query.filter(models.Complaint.created_at >= df)
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.strptime(date_to, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
            query = query.filter(models.Complaint.created_at <= dt)
        except ValueError:
            pass

    total = query.count()
    items = query.order_by(models.Complaint.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": items}


@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(
    complaint_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    c = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if c.user_id != current_user.id and current_user.role not in ("admin", "employee"):
        raise HTTPException(status_code=403, detail="Access denied")
    return c


@router.get("/{complaint_id}/history")
def get_status_history(
    complaint_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    c = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if c.user_id != current_user.id and current_user.role not in ("admin", "employee"):
        raise HTTPException(status_code=403, detail="Access denied")

    history = (
        db.query(models.ComplaintStatusHistory)
        .filter(models.ComplaintStatusHistory.complaint_id == complaint_id)
        .order_by(models.ComplaintStatusHistory.created_at.asc())
        .all()
    )
    return [
        {
            "id":              h.id,
            "status":          h.status,
            "changed_by_name": h.changed_by_name,
            "changed_by_role": h.changed_by_role,
            "note":            h.note,
            "created_at":      h.created_at.isoformat() if h.created_at else "",
        }
        for h in history
    ]


@router.post("/{complaint_id}/rate", response_model=schemas.ComplaintOut)
def rate_complaint(
    complaint_id: str,
    data: schemas.ComplaintRate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if not 1 <= data.rating <= 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    c = db.query(models.Complaint).filter(models.Complaint.complaint_id == complaint_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if c.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only rate your own complaints")
    if c.status != "Resolved":
        raise HTTPException(status_code=400, detail="Only resolved complaints can be rated")
    if c.satisfaction_rating is not None:
        raise HTTPException(status_code=400, detail="You have already rated this complaint")
    c.satisfaction_rating = data.rating
    db.commit()
    db.refresh(c)
    return c
