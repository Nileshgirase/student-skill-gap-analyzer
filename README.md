# Student Skill Gap Analyzer and Personalized Learning Roadmap Provider

A full-stack, portfolio-level web application designed to help students analyze real, verified job requirements for their target roles at chosen companies, assess their personal skill gaps with evidence-based comparisons, and generate actionable, time-bounded learning roadmaps using verified free resources.

---

## 📌 Project Overview & Non-Negotiable Principles

1. **No Fabricated Requirements**: The system never infers or invents job requirements. All required skills are linked directly to evidence excerpts from verified job descriptions.
2. **Current Source Data**: Analyses are initiated against real, permitted source connectors (official career portals, public feeds) rather than static company-to-skill mappings.
3. **Free & Open-Source First**: Built completely without paid APIs, paid AI models, or paid authentication services.
4. **Honest UX**: Clear distinctions between required, preferred, and student self-reported skills, with explicit statuses when no matching jobs or descriptions are found.

---

## 🏗️ Implementation Status

| Phase | Milestone | Status |
| :--- | :--- | :--- |
| **Phase 1** | **Backend Foundation (FastAPI, SQLite, Health Endpoint, Pytest)** | **Completed** |
| **Phase 2** | **Authentication & User Management (Argon2, JWT, /api/auth/me)** | **Completed** |
| **Phase 3** | **Analysis Input & Persistence (Ownership Scoping, Models, Endpoints)** | **Completed** |
| **Phase 4** | **First Verified Source Connector (Normalized Job Architecture, Greenhouse)** | **Completed** |
| **Phase 5** | **Multi-Source Connectors (Lever ATS, Deduplication & Freshness Policy)** | **Completed** |
| **Phase 6** | **Skill Extraction & Gap Analysis Engine (Evidence Tracking & Coverage)** | **Completed** |
| Phase 7 | Personalized Learning Roadmap Generator | Pending approval |
| Phase 7 | Personalized Learning Roadmap Generator | Pending |
| Phase 8 | Frontend Web Application (React + Vite + Tailwind CSS) | Pending |
| Phase 9 | Hardening & Portfolio Documentation | Pending |

---

## 📁 Repository Structure (Phase 1)

```text
E:\Skill Analyzer\
├── backend\
│   ├── app\
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI entry point & CORS configuration
│   │   ├── config.py          # Pydantic Settings & environment loader
│   │   ├── database.py        # SQLAlchemy engine, session maker & SQLite setup
│   │   └── routes\
│   │       ├── __init__.py
│   │       └── health.py      # Health-check endpoint (/api/health)
│   ├── tests\
│   │   ├── __init__.py
│   │   ├── conftest.py        # Pytest fixtures & isolated in-memory test DB
│   │   └── test_health.py     # Health-check & DB connectivity tests
│   ├── .env.example           # Environment template
│   ├── .env                   # Local development configuration (git-ignored)
│   ├── requirements.txt       # Python dependencies
│   └── venv\                  # Python virtual environment (git-ignored)
├── .gitignore
├── README.md
└── student_skill_gap_analyzer_ai_coding_agent_instructions.md
```

---

## 🚀 Getting Started (Windows PowerShell)

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Windows PowerShell

### 1. Set Up Virtual Environment & Install Dependencies

From the workspace root directory:

```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> **PowerShell Execution Policy Note**:
> If running `.\venv\Scripts\Activate.ps1` gives an execution policy error, run this scoped command in your current PowerShell session:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> ```

### 2. Configure Environment Variables

The backend loads configuration from `backend/.env`. A development `.env` is created automatically from `.env.example`:

```dotenv
APP_NAME="Student Skill Gap Analyzer"
ENVIRONMENT="development"
DATABASE_URL="sqlite:///./app.db"
JWT_SECRET="dev_secret_key_student_skill_gap_analyzer_only"
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_ORIGIN="http://localhost:5173"
```

### 3. Run the Backend Server

```powershell
# From the backend directory with venv activated:
uvicorn app.main:app --reload
```

- API Base URL: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive API Docs (Swagger UI): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Alternative API Docs (ReDoc): [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Health Check Endpoint: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 📡 API Endpoints (Phases 1, 2, 3, 4 & 6)

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/` | No | API discovery information & quick links |
| `GET` | `/api/health` | No | Health check & active SQLite database connectivity probe |
| `POST` | `/api/auth/register` | No | Register new student, hashes password with Argon2, returns JWT |
| `POST` | `/api/auth/login` | No | Authenticate credentials and receive JWT bearer token |
| `GET` | `/api/auth/me` | **Yes** (Bearer) | Get current student user profile (safe, never returns password) |
| `POST` | `/api/analyses` | **Yes** (Bearer) | Create new analysis (company, role, study hours, self-reported skills) |
| `GET` | `/api/analyses` | **Yes** (Bearer) | List all prior analyses for authenticated student |
| `GET` | `/api/analyses/{id}` | **Yes** (Bearer) | Retrieve analysis by ID with skills and snapshots |
| `DELETE` | `/api/analyses/{id}` | **Yes** (Bearer) | Delete owned analysis with cascade deletion of related records |
| `POST` | `/api/analyses/{id}/student-skills` | **Yes** (Bearer) | Replace or update student skills for an owned analysis |
| `POST` | `/api/analyses/{id}/search-jobs` | **Yes** (Bearer) | Retrieve verified job postings from permitted ATS sources |
| `POST` | `/api/analyses/{id}/run-gap-analysis` | **Yes** (Bearer) | Run evidence-backed skill extraction, gap comparison & coverage score |

---

### 4. Run the Test Suite

```powershell
# From the backend directory with venv activated:
pytest -v
```

All tests run in-memory against an isolated SQLite test database without affecting local development data.
