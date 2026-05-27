# SmartComplaints — AI-Powered Complaint Management System

A full-stack complaint management system that uses machine learning to automatically classify complaints into categories and assign priority levels.

## Features

- **AI Classification** — Automatically categorizes complaints (Account Issue, Payment Issue, Delivery Issue, Product Issue, Refund Request, Customer Service, Product Inquiry) and assigns High / Medium / Low priority using a trained ML model
- **Role-based Access** — Three roles: Customer, Employee, Admin
- **Real-time Chat** — WebSocket-based chat per complaint between customers and support agents
- **Status Tracking** — Full complaint lifecycle with status history (Open → In Progress → Escalated → Resolved)
- **Email Notifications** — Sends email on complaint submission and status updates via Gmail SMTP
- **Admin Dashboard** — Analytics, agent workload, category-to-agent assignments, user management
- **Image Attachments** — Customers can attach photos to complaints
- **Satisfaction Ratings** — Customers can rate resolved complaints

## Tech Stack

### Backend
- Python 3.x
- FastAPI
- SQLAlchemy + SQLite
- scikit-learn (ML classification)
- NLTK (text preprocessing)
- JWT authentication (python-jose)
- Gmail SMTP (email notifications)

### Frontend
- React + Vite
- Tailwind CSS
- React Router
- Axios
- WebSockets

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/kkartikkkk/Mini-Project-Sem-6-.git
cd Mini-Project-Sem-6-/complaint-system
```

### 2. Backend Setup

```bash
cd backend
pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib[bcrypt] python-multipart pandas openpyxl scikit-learn nltk aiofiles
```

Train the ML models (requires the dataset file):
```bash
python train_model.py
```

Create the admin user:
```bash
python seed_admin.py
```

Start the backend:
```bash
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### 3. Email Setup (Optional)

Set these environment variables before starting the backend to enable email notifications:

```bash
set GMAIL_USER=youremail@gmail.com
set GMAIL_APP_PASSWORD=your_gmail_app_password
```

Generate a Gmail App Password at: Google Account → Security → 2-Step Verification → App Passwords

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

## Default Admin Login

```
Email:    admin@example.com
Password: admin123
```

## Project Structure

```
complaint-system/
├── backend/
│   ├── main.py               # FastAPI app entry point
│   ├── models.py             # Database models
│   ├── schemas.py            # Pydantic schemas
│   ├── ml_service.py         # ML classification logic
│   ├── email_service.py      # Gmail email notifications
│   ├── train_model.py        # Train sklearn models
│   ├── routers/
│   │   ├── complaints.py     # Complaint CRUD
│   │   ├── admin.py          # Admin endpoints
│   │   ├── chat.py           # WebSocket chat
│   │   └── auth_router.py    # Auth endpoints
│   └── uploads/              # Uploaded images
└── frontend/
    └── src/
        ├── pages/            # React pages
        ├── components/       # Shared components
        └── context/          # Auth & Theme context
```
