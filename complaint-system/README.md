# 🎯 Smart Complaint Handling System for E-Commerce

A full-stack AI-powered complaint management system that automatically classifies incoming complaints by category and priority, routes them to the right agents, and keeps customers informed via email.

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.10+ |
| Database | SQLite (swappable to MySQL via env var) |
| Frontend | React 18 + Vite + Tailwind CSS + Recharts |
| ML / NLP | FastText (primary) → sklearn TF-IDF + Logistic Regression (fallback) → Rule-based engine |
| Auth | JWT — python-jose + bcrypt |
| Email | Brevo SMTP relay via smtplib (no extra packages) |
| Real-time | WebSockets (live chat between admin and customer) |

---

## 🚀 Quick Start

### 1. Backend

```bash
cd complaint-system/backend

# Install dependencies
pip install -r requirements.txt

# (Optional) Train the FastText model for best accuracy
pip install fasttext-wheel openpyxl
python train_fasttext.py
# Generates complaint_fasttext.bin — if skipped, falls back to sklearn/rule-based

# Seed the default admin account
python seed_admin.py

# Start the API server
python -m uvicorn main:app --reload --port 8001
```

API docs: http://localhost:8001/docs

### 2. Frontend

```bash
cd complaint-system/frontend
npm install
npm run dev
```

App: http://localhost:5173

---

## 🔐 Default Accounts

| Role | Email | Password |
|------|-------|----------|
| Main Admin | admin@demo.com | admin123 |

Register new users via the UI — they get the `user` role by default.
Promote users to `employee` (agent) or `admin` from the Users panel.

---

## 📧 Email Notifications (Optional)

Customers receive emails when:
- A complaint is **submitted** (confirmation with complaint ID, category, priority)
- An admin **changes the status** (Open → In Progress → Escalated → Resolved)

Emails are sent via **Brevo** (free tier: 300 emails/day) which has SPF/DKIM configured so they land in the inbox, not spam.

Setup:
1. Create a free account at https://app.brevo.com
2. Go to **Account → SMTP & API → SMTP tab**
3. Copy your SMTP login (your Brevo account email) and click **Generate an SMTP key**
4. Add to `backend/.env`:

```env
BREVO_SMTP_USER=youremail@gmail.com
BREVO_SMTP_KEY=your-brevo-smtp-key
BREVO_SENDER_NAME=SmartComplaints
```

If not configured, emails are silently skipped and everything else works normally.

---

## 🤖 ML Classification Pipeline

Complaints go through a 4-tier pipeline (in order of priority):

```
1. Rule-based engine   → Handles Payment Issue & Product Inquiry
                          (absent from training data; strong keyword signals)
2. FastText model      → Handles the 6 dataset categories with high accuracy
3. sklearn fallback    → Used if FastText model file is not present
4. Rule-based default  → Last resort if no models are available
```

**Categories:** Delivery Issue · Payment Issue · Product Issue · Account Issue · Refund Request · Customer Service · Product Inquiry

**Priorities:** High · Medium · Low (each category has a minimum floor — e.g. Account Issue is always at least High)

**Fuzzy correction:** Misspelled words are corrected before classification using `difflib.get_close_matches`.

### Training FastText

```bash
cd backend
python train_fasttext.py
```

Reads `ecommerce_consumer_complaints_5000.xlsx`, trains for 50 epochs, saves `complaint_fasttext.bin`.

---

## 🗂️ Project Structure

```
complaint-system/
├── backend/
│   ├── main.py                  ← FastAPI entry point + SLA background task
│   ├── database.py              ← SQLAlchemy + SQLite setup
│   ├── models.py                ← ORM models (User, Complaint, StatusHistory, etc.)
│   ├── schemas.py               ← Pydantic request/response schemas
│   ├── auth.py                  ← JWT authentication + role guards
│   ├── ml_service.py            ← 4-tier NLP classifier
│   ├── email_service.py         ← Gmail SMTP email notifications
│   ├── train_fasttext.py        ← FastText model training script
│   ├── train_model.py           ← sklearn fallback model training script
│   ├── seed_admin.py            ← Create default admin account
│   ├── requirements.txt
│   └── routers/
│       ├── auth_router.py       ← /api/auth/*
│       ├── complaints.py        ← /api/complaints/*
│       └── admin.py             ← /api/admin/*
└── frontend/
    └── src/
        ├── App.jsx              ← Routes
        ├── api/axios.js         ← Axios instance with JWT interceptor
        ├── context/
        │   ├── AuthContext.jsx  ← Auth state + login/logout
        │   └── ThemeContext.jsx ← Dark/light mode
        ├── pages/
        │   ├── Login.jsx
        │   ├── Register.jsx
        │   ├── Dashboard.jsx           ← Customer dashboard
        │   ├── SubmitComplaint.jsx     ← Submit with AI category preview
        │   ├── MyComplaints.jsx        ← Complaint list with search + date filter
        │   ├── UserComplaintDetail.jsx ← Customer complaint detail + live chat
        │   ├── AdminDashboard.jsx      ← Admin overview + charts
        │   ├── AdminComplaints.jsx     ← Manage all complaints (filter/search)
        │   ├── AdminComplaintDetail.jsx← Update status/priority + internal notes
        │   ├── Analytics.jsx           ← Deep analytics + category breakdown
        │   ├── AdminUsers.jsx          ← User management (roles, activate/disable)
        │   ├── AdminAssignments.jsx    ← Assign complaint categories to agents
        │   └── AdminWorkload.jsx       ← Agent workload overview
        └── components/
            ├── Navbar.jsx
            ├── PrivateRoute.jsx
            ├── ComplaintCard.jsx
            └── ChatPanel.jsx           ← WebSocket live chat
```

---

## 🌐 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login + get JWT |
| GET | /api/auth/me | Get current user |

### Complaints (Customer)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/complaints/ | Submit complaint (AI classified) |
| GET | /api/complaints/my | My complaints (search + date + status filter) |
| GET | /api/complaints/{id} | Complaint detail |
| GET | /api/complaints/{id}/history | Status change timeline |
| POST | /api/complaints/{id}/rate | Rate resolved complaint (1–5 stars) |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/admin/complaints | All complaints (filter by status/priority/category/SLA) |
| PATCH | /api/admin/complaints/{id} | Update status, priority, notes, assignee |
| GET | /api/admin/analytics | Analytics summary |
| GET | /api/admin/export | Download all complaints as CSV |
| GET | /api/admin/users | List all users |
| PATCH | /api/admin/users/{id}/toggle | Enable / disable user |
| PATCH | /api/admin/users/{id}/role | Change user role |
| GET | /api/admin/agents | List agents eligible for assignment |
| GET | /api/admin/assignments | Category → agent mappings |
| PUT | /api/admin/assignments/{category} | Set agent for a category |
| GET | /api/admin/workload | Open complaint counts per agent |
| POST | /api/admin/sla/check | Manually trigger SLA check |

---

## 🔔 Features

- **AI classification** — complaint text is automatically categorised and prioritised on submission
- **Email notifications** — customers get a confirmation on submit and an update on every status change
- **Live chat** — WebSocket-based chat between customer and admin on each complaint
- **SLA tracking** — complaints auto-escalate and are flagged if unresolved past SLA threshold
- **Agent assignment** — map complaint categories to specific agents; new complaints auto-assign
- **Agent workload view** — see open/resolved/high-priority counts per agent to rebalance load
- **Complaint search** — customers can filter their history by keyword, date range, and status
- **Satisfaction ratings** — customers rate resolved complaints 1–5 stars
- **CSV export** — download full complaint history
- **Dark mode** — toggle from the navbar
- **Role-based access** — `user` (customer), `employee` (agent), `admin` (main admin)

---

## 🗄️ Using MySQL (Production)

Add to your environment before starting the backend:

```bash
DATABASE_URL=mysql+mysqlconnector://user:password@localhost/complaints_db
```
