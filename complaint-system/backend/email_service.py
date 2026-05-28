import os
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

GMAIL_USER     = os.environ.get("GMAIL_USER", "")

GMAIL_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

SENDER_NAME    = "SmartComplaints"

EMAIL_ENABLED  = bool(GMAIL_USER and GMAIL_PASSWORD)

if EMAIL_ENABLED:
    print(f"[Email Service] Gmail ready → {GMAIL_USER} ✓")

else:
    print("[Email Service] GMAIL_USER / GMAIL_APP_PASSWORD not set — emails disabled.")

STATUS_META = {
    "Open": {
        "emoji":   "📝",
        "label":   "Submitted",
        "color":   "#3b82f6",
        "bg":      "#eff6ff",
        "message": "We have received your complaint and it is in our queue.",
    },
    "In Progress": {
        "emoji":   "🔍",
        "label":   "Under Review",
        "color":   "#7c3aed",
        "bg":      "#f5f3ff",
        "message": "Our support team is actively investigating your issue.",
    },
    "Escalated": {
        "emoji":   "🚨",
        "label":   "Escalated",
        "color":   "#dc2626",
        "bg":      "#fef2f2",
        "message": "Your complaint has been escalated to our senior team for priority resolution.",
    },
    "Resolved": {
        "emoji":   "✅",
        "label":   "Resolved",
        "color":   "#16a34a",
        "bg":      "#f0fdf4",
        "message": "Great news! Your complaint has been resolved.",
    },
}

PRIORITY_COLORS = {
    "High":   "#f97316",
    "Medium": "#d97706",
    "Low":    "#16a34a",
}


def _build_html(complaint_id, user_name, status, priority, complaint_text,
                resolution_note, old_status):
    meta     = STATUS_META.get(status, STATUS_META["Open"])

    p_color  = PRIORITY_COLORS.get(priority, "#6b7280")

    now_str  = datetime.now().strftime("%d %b %Y, %I:%M %p")

    short_text = complaint_text[:120] + ("…" if len(complaint_text) > 120 else "")

    resolution_block = ""

    if resolution_note and status == "Resolved":
        resolution_block = f"""
        <div style="background:#f0fdf4;border-left:4px solid #16a34a;padding:12px 16px;
                    border-radius:0 8px 8px 0;margin-top:16px;">
          <p style="margin:0 0 4px;font-size:12px;color:#15803d;font-weight:600;">
            📢 Resolution from Support Team
          </p>
          <p style="margin:0;font-size:14px;color:#166534;line-height:1.5;">
            {resolution_note}
          </p>
        </div>"""

    change_line = ""

    if old_status and old_status != status:
        change_line = f"""
        <p style="margin:0 0 16px;font-size:13px;color:#6b7280;">
          Status changed:
          <span style="background:#f3f4f6;padding:2px 8px;border-radius:4px;font-weight:600;">
            {old_status}
          </span>
          &nbsp;→&nbsp;
          <span style="background:{meta['bg']};color:{meta['color']};padding:2px 8px;
                       border-radius:4px;font-weight:600;">
            {status}
          </span>
        </p>"""

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:40px 20px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

        <tr><td style="background:linear-gradient(135deg,#1d4ed8,#3b82f6);
                        border-radius:12px 12px 0 0;padding:28px 32px;text-align:center;">
          <p style="margin:0;font-size:22px;font-weight:700;color:#fff;letter-spacing:-0.3px;">
            🎯 SmartComplaints
          </p>
          <p style="margin:6px 0 0;font-size:13px;color:#bfdbfe;">
            Complaint Status Update
          </p>
        </td></tr>

        <tr><td style="background:#fff;padding:32px;border-left:1px solid #e5e7eb;
                        border-right:1px solid #e5e7eb;">

          <p style="margin:0 0 8px;font-size:16px;color:#111827;">
            Hi <strong>{user_name}</strong>,
          </p>
          <p style="margin:0 0 24px;font-size:14px;color:#6b7280;line-height:1.6;">
            Your complaint <strong style="color:#1d4ed8;">{complaint_id}</strong>
            has been updated. Here's the latest status:
          </p>

          <div style="background:{meta['bg']};border:2px solid {meta['color']}22;
                      border-radius:12px;padding:20px 24px;margin-bottom:24px;text-align:center;">
            <div style="font-size:36px;margin-bottom:8px;">{meta['emoji']}</div>
            <p style="margin:0;font-size:20px;font-weight:700;color:{meta['color']};">
              {meta['label']}
            </p>
            <p style="margin:8px 0 0;font-size:13px;color:{meta['color']};opacity:.8;">
              {meta['message']}
            </p>
          </div>

          {change_line}

          <table width="100%" cellpadding="0" cellspacing="0"
                 style="background:#f9fafb;border-radius:8px;padding:16px;margin-bottom:8px;">
            <tr>
              <td style="padding:4px 0;font-size:12px;color:#9ca3af;width:120px;">Complaint ID</td>
              <td style="padding:4px 0;font-size:13px;color:#111827;font-family:monospace;
                          font-weight:600;">{complaint_id}</td>
            </tr>
            <tr>
              <td style="padding:4px 0;font-size:12px;color:#9ca3af;">Priority</td>
              <td style="padding:4px 0;">
                <span style="font-size:12px;font-weight:700;color:{p_color};">{priority}</span>
              </td>
            </tr>
            <tr>
              <td style="padding:4px 0;font-size:12px;color:#9ca3af;vertical-align:top;">
                Your Message
              </td>
              <td style="padding:4px 0;font-size:13px;color:#374151;line-height:1.5;">
                {short_text}
              </td>
            </tr>
            <tr>
              <td style="padding:4px 0;font-size:12px;color:#9ca3af;">Updated At</td>
              <td style="padding:4px 0;font-size:13px;color:#6b7280;">{now_str}</td>
            </tr>
          </table>

          {resolution_block}

        </td></tr>

        <tr><td style="background:#f3f4f6;border-radius:0 0 12px 12px;
                        border:1px solid #e5e7eb;border-top:none;
                        padding:20px 32px;text-align:center;">
          <p style="margin:0;font-size:12px;color:#9ca3af;line-height:1.6;">
            This email was sent automatically by SmartComplaints.<br>
            Please do not reply to this email.
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>

</body>
</html>"""


def _build_plain(complaint_id, user_name, status, priority, complaint_text,
                 resolution_note, old_status):
    meta = STATUS_META.get(status, STATUS_META["Open"])

    lines = [
        "SmartComplaints — Complaint Status Update",
        "",
        f"Hi {user_name},",
        "",
        f"Your complaint {complaint_id} has been updated.",
        f"Status   : {meta['label']}",
        f"Priority : {priority}",
        "",
        meta["message"],
    ]

    if old_status and old_status != status:
        lines.insert(4, f"Changed    : {old_status} → {status}")

    if resolution_note and status == "Resolved":
        lines += ["", "Resolution:", resolution_note]

    lines += ["", "— SmartComplaints Support Team"]

    return "\n".join(lines)


def _send(to_email, subject, html, plain):
    try:
        msg = MIMEMultipart("alternative")

        msg["Subject"] = subject

        msg["From"]    = f"{SENDER_NAME} <{GMAIL_USER}>"

        msg["To"]      = to_email

        msg.attach(MIMEText(plain, "plain"))

        msg.attach(MIMEText(html,  "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)

            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        print(f"[Email Service] ✓ Sent to {to_email} — {subject}")

    except Exception as e:
        print(f"[Email Service] ✗ Failed to send to {to_email}: {e}")


def send_submission_email(
    to_email: str,
    user_name: str,
    complaint_id: str,
    category: str,
    priority: str,
    complaint_text: str,
    resolution_note: str = "",
):
    if not EMAIL_ENABLED:
        print(f"[Email Service] Skipped (not configured) — would email {to_email}")

        return

    p_color   = PRIORITY_COLORS.get(priority, "#6b7280")

    now_str   = datetime.now().strftime("%d %b %Y, %I:%M %p")

    short_text = complaint_text[:120] + ("…" if len(complaint_text) > 120 else "")

    priority_bg = {"High": "#fff7ed", "Medium": "#fffbeb", "Low": "#f0fdf4"}.get(priority, "#f9fafb")

    resolution_block = ""

    if resolution_note:
        resolution_block = f"""
        <div style="background:#eff6ff;border-left:4px solid #3b82f6;padding:12px 16px;
                    border-radius:0 8px 8px 0;margin-top:16px;">
          <p style="margin:0 0 4px;font-size:12px;color:#1d4ed8;font-weight:600;">
            💡 What happens next?
          </p>
          <p style="margin:0;font-size:14px;color:#1e40af;line-height:1.5;">
            {resolution_note}
          </p>
        </div>"""

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9fafb;padding:40px 20px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

        <tr><td style="background:linear-gradient(135deg,#1d4ed8,#3b82f6);
                        border-radius:12px 12px 0 0;padding:28px 32px;text-align:center;">
          <p style="margin:0;font-size:22px;font-weight:700;color:#fff;letter-spacing:-0.3px;">
            🎯 SmartComplaints
          </p>
          <p style="margin:6px 0 0;font-size:13px;color:#bfdbfe;">
            Complaint Received — We're on it!
          </p>
        </td></tr>

        <tr><td style="background:#fff;padding:32px;border-left:1px solid #e5e7eb;
                        border-right:1px solid #e5e7eb;">

          <p style="margin:0 0 8px;font-size:16px;color:#111827;">
            Hi <strong>{user_name}</strong>,
          </p>
          <p style="margin:0 0 24px;font-size:14px;color:#6b7280;line-height:1.6;">
            Thank you for reaching out. We've received your complaint and our support team
            is already on it. Here's a summary of what you submitted:
          </p>

          <div style="background:#eff6ff;border:2px solid #3b82f622;
                      border-radius:12px;padding:20px 24px;margin-bottom:24px;text-align:center;">
            <div style="font-size:36px;margin-bottom:8px;">📝</div>
            <p style="margin:0;font-size:20px;font-weight:700;color:#1d4ed8;">
              Complaint Submitted
            </p>
            <p style="margin:8px 0 0;font-size:13px;color:#3b82f6;">
              Your complaint has been logged and assigned a tracking ID.
            </p>
          </div>

          <table width="100%" cellpadding="0" cellspacing="0"
                 style="background:#f9fafb;border-radius:8px;padding:16px;margin-bottom:8px;">
            <tr>
              <td style="padding:4px 0;font-size:12px;color:#9ca3af;width:120px;">Complaint ID</td>
              <td style="padding:4px 0;font-size:13px;color:#111827;font-family:monospace;font-weight:600;">
                {complaint_id}
              </td>
            </tr>
            <tr>
              <td style="padding:4px 0;font-size:12px;color:#9ca3af;">Category</td>
              <td style="padding:4px 0;">
                <span style="font-size:12px;font-weight:600;color:#4f46e5;
                             background:#eef2ff;padding:2px 8px;border-radius:4px;">
                  {category}
                </span>
              </td>
            </tr>
            <tr>
              <td style="padding:4px 0;font-size:12px;color:#9ca3af;">Priority</td>
              <td style="padding:4px 0;">
                <span style="font-size:12px;font-weight:700;color:{p_color};
                             background:{priority_bg};padding:2px 8px;border-radius:4px;">
                  {priority}
                </span>
              </td>
            </tr>
            <tr>
              <td style="padding:4px 0;font-size:12px;color:#9ca3af;vertical-align:top;">Your Message</td>
              <td style="padding:4px 0;font-size:13px;color:#374151;line-height:1.5;">
                {short_text}
              </td>
            </tr>
            <tr>
              <td style="padding:4px 0;font-size:12px;color:#9ca3af;">Submitted At</td>
              <td style="padding:4px 0;font-size:13px;color:#6b7280;">{now_str}</td>
            </tr>
          </table>

          {resolution_block}

        </td></tr>

        <tr><td style="background:#f3f4f6;border-radius:0 0 12px 12px;
                        border:1px solid #e5e7eb;border-top:none;
                        padding:20px 32px;text-align:center;">
          <p style="margin:0;font-size:12px;color:#9ca3af;line-height:1.6;">
            You'll receive another email when your complaint status is updated.<br>
            This email was sent automatically by SmartComplaints. Please do not reply.
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>

</body>
</html>"""

    plain = "\n".join([
        "SmartComplaints — Complaint Received",
        "",
        f"Hi {user_name}, thank you for submitting your complaint.",
        "",
        f"Complaint ID : {complaint_id}",
        f"Category     : {category}",
        f"Priority     : {priority}",
        f"Submitted At : {now_str}",
        f"Your Message : {short_text}",
        "",
        resolution_note or "Our team will review your complaint and get back to you shortly.",
        "",
        "You'll receive updates by email as your case progresses.",
        "",
        "— SmartComplaints Support Team",
    ])

    subject = f"📝 [{complaint_id}] Complaint Received — We're on it!"

    thread = threading.Thread(
        target=_send, args=(to_email, subject, html, plain), daemon=True
    )

    thread.start()


def send_status_email(
    to_email: str,
    user_name: str,
    complaint_id: str,
    status: str,
    priority: str,
    complaint_text: str,
    resolution_note: str = "",
    old_status: str = "",
):
    if not EMAIL_ENABLED:
        print(f"[Email Service] Skipped (not configured) — would email {to_email}")

        return

    meta    = STATUS_META.get(status, STATUS_META["Open"])

    subject = f"{meta['emoji']} [{complaint_id}] Status Update: {meta['label']}"

    html  = _build_html(complaint_id, user_name, status, priority,
                        complaint_text, resolution_note, old_status)

    plain = _build_plain(complaint_id, user_name, status, priority,
                         complaint_text, resolution_note, old_status)

    thread = threading.Thread(target=_send, args=(to_email, subject, html, plain), daemon=True)

    thread.start()


