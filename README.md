# RecruitAI 🚀

An AI-powered recruitment platform that streamlines the hiring process with intelligent resume analysis and automated candidate shortlisting.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### For HR
- **Job Posting Management** - Create, edit, and delete job postings
- **AI-Powered Resume Analysis** - Automatic scoring and gap analysis for each applicant
- **Smart Shortlisting** - Select top N candidates by AI score with one click
- **Automated Email Notifications** - Send interview invitations to selected candidates
- **HR Summary Reports** - Receive email summaries with all shortlisted candidates

### For Applicants
- **Easy Application** - Upload resume and apply to jobs
- **AI Feedback** - View your resume score and skill gaps
- **Application Tracking** - Monitor application status

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, SQLAlchemy, PostgreSQL |
| AI/ML | LangChain, Groq/Google AI, Sentence Transformers |
| Frontend | HTML, CSS, JavaScript |
| Email | Gmail SMTP (Free) |
| Storage | Local / Supabase |

## 📁 Project Structure

```
Recruitment/
├── backend/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models/              # SQLAlchemy models
│   ├── routes/              # API endpoints
│   ├── schemas/             # Pydantic schemas
│   └── services/            # Business logic
│       ├── email_service.py # Email notifications
│       ├── resume_analyzer.py # AI resume analysis
│       └── storage.py       # File storage
├── frontend/
│   ├── index.html           # Landing page
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── hr-dashboard.html    # HR dashboard
│   ├── applicant-dashboard.html # Applicant dashboard
│   ├── jobs.html            # Job listings
│   ├── css/                 # Stylesheets
│   └── js/                  # JavaScript files
├── .env                     # Environment variables
└── requirements.txt         # Python dependencies
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/bilaljaved942/Recruitement.git
cd Recruitement
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
pip install pydantic[email]
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/recruitment_db

# JWT Secret
JWT_SECRET=your-super-secret-key-change-in-production

# AI (Choose one)
GROQ_API_KEY=your-groq-api-key
GOOGLE_API_KEY=your-google-api-key

# Email (Gmail SMTP - Free)
SMTP_EMAIL=your-gmail@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

> 📧 **Gmail App Password**: Enable 2FA on your Gmail account, then generate an app password at https://myaccount.google.com/apppasswords

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 5500
```

### 6. Access the Application
- **Frontend**: http://127.0.0.1:5500
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| GET | `/auth/me` | Get current user |

### Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/jobs` | List all active jobs |
| POST | `/jobs` | Create job (HR only) |
| PUT | `/jobs/{id}` | Update job (HR only) |
| DELETE | `/jobs/{id}` | Delete job (HR only) |

### Applications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/applications` | Apply to job with resume |
| GET | `/applications/my-applications` | Get user's applications |
| GET | `/applications/job/{job_id}` | Get applications for job (HR) |
| POST | `/applications/job/{job_id}/shortlist-and-notify` | **Shortlist top N & send emails** |

## 📧 Shortlist & Email Feature

The key feature allows HR to:
1. View all applications sorted by AI score
2. Enter threshold (e.g., top 10 candidates)
3. Click "Shortlist & Send Emails"
4. System automatically:
   - Selects top N candidates by score
   - Updates their status to "Shortlisted"
   - Sends interview invitation emails to candidates
   - Sends summary email to HR with all selected candidates

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

Made with ❤️ using FastAPI and AI
