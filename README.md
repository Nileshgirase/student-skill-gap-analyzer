# Student Skill Gap Analyzer & Personalized Learning Roadmap Provider

> **Portfolio-Grade Full-Stack Web Application** built with **FastAPI**, **SQLAlchemy**, **SQLite**, **React 18**, **Vite 6**, and **Tailwind CSS v4**.
> Designed with strict adherence to evidence-based extraction, transparent metrics, and zero-fabrication principles.

---

## 📑 Table of Contents
1. [Core Non-Negotiable Principles](#-core-non-negotiable-principles)
2. [End-to-End System Architecture](#-end-to-end-system-architecture)
3. [Technology Stack](#-technology-stack)
4. [Project Structure](#-project-structure)
5. [Local Development Setup (Windows PowerShell)](#-local-development-setup-windows-powershell)
6. [Automated Test Suite](#-automated-test-suite)
7. [REST API Reference](#-rest-api-reference)
8. [Engine & Algorithm Specifications](#-engine--algorithm-specifications)
   - [Explainable Token Relevance](#1-explainable-token-relevance)
   - [Disambiguated Evidence Extraction](#2-disambiguated-evidence-extraction)
   - [Skill-Gap Categorization & Coverage Formula](#3-skill-gap-categorization--coverage-formula)
   - [Weekly Budget-Constrained Roadmap Scheduling](#4-weekly-budget-constrained-roadmap-scheduling)
   - [IT Domain Role Validation & Typo Tolerance](#5-it-domain-role-validation--typo-tolerance)
9. [Extensibility Guide](#-extensibility-guide)
   - [Adding a New Permitted Source Connector](#adding-a-new-permitted-job-connector)
   - [Adding New Curated Learning Resources](#adding-new-curated-learning-resources)
10. [Limitations, Privacy & Ethical Compliance](#-limitations-privacy--ethical-compliance)
11. [Production Deployment & Database Persistence (Render Free Tier)](#-production-deployment--database-persistence-render-free-tier)

---

## 🎯 Core Non-Negotiable Principles

1. **Zero Hallucination / No Fabricated Requirements**:
   The engine never invents or synthesizes job requirements or skills. Every extracted technical requirement is explicitly tied to a verifiable sentence-level excerpt from an official job posting.
2. **Current Source Provenance**:
   Instead of relying on static, outdated company-to-skill mock mappings, searches query live public ATS feeds (Greenhouse & Lever) in real-time, recording fetch timestamps and freshness status.
3. **100% Free & Open-Source Tools**:
   Zero paid APIs, zero proprietary LLM tokens, zero paid authentication services, and zero subscription databases. The entire stack runs self-contained on local hardware.
4. **Honest, Explanatory Metrics**:
   The skill coverage score is an explanatory comparison against explicitly stated job requirements, never a promise or guarantee of employability. If no verified jobs or requirements exist, the system returns an honest `null` / empty status rather than a false 0% or fake score.
5. **Free-Text Employer & Role Inputs**:
   Students are never confined to predefined drop-down selections. They can input any employer name and any job title.

---

## 🏛️ End-to-End System Architecture

```mermaid
flowchart TD
    User["Student User"] -->|Free-text Company, Role & Skills| FE["React 18 SPA (Vite + Tailwind v4)"]
    FE -->|Authenticated REST API Requests (JWT)| BE["FastAPI Application"]
    
    subgraph Data Acquisition & Aggregation
        BE -->|Company & Role Query| Agg["Job Aggregation Service"]
        Agg -->|Public Board API| GH["Greenhouse Connector"]
        Agg -->|Public Board API| LV["Lever Connector"]
        GH --> Clean["HTML Sanitizer & Token Relevance Scorer"]
        LV --> Clean
        Clean --> Dedup["Cross-Platform Deduplication & Freshness Policy"]
        Dedup --> DB_Snap["SQLite Job Snapshots Table"]
    end

    subgraph Skill Extraction & Gap Engine
        DB_Snap --> Extractor["Contextual Disambiguation & Sentence Evidence Extractor"]
        Extractor --> Gap["Taxonomy Matcher & Gap Classifier"]
        Gap --> Metric["Coverage Metric Calculator (Strict Required Only)"]
        Metric --> DB_Skills["SQLite Required Skills Table"]
    end

    subgraph Personalized Roadmap Synthesis
        DB_Skills --> Scheduler["Priority Scheduler & Weekly Budget Bounded Engine"]
        Cat[("Curated Free Learning Catalog")] --> Scheduler
        Scheduler --> DB_Roadmap["SQLite Roadmap Items Table"]
    end

    DB_Roadmap -->|Week-by-week actionable plan| FE
    DB_Skills -->|Evidence-backed cards & coverage score| FE
```

---

## 💻 Technology Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** | `^0.115.0` | High-performance asynchronous REST API framework |
| **Language** | **Python** | `3.10+` (tested on `3.13`) | Core backend runtime and natural language processing |
| **Database & ORM** | **SQLAlchemy** + **PostgreSQL** / **SQLite** | `^2.0.0` | Relational models, connection pooling, SQLite for dev, PostgreSQL (`psycopg2-binary`) for production persistence |
| **Password Security** | **Argon2id** (`pwdlib`) | `^0.2.0` | Modern, GPU-resistant memory-hard password hashing |
| **Authentication** | **PyJWT** | `^2.10.0` | Stateless HMAC-SHA256 bearer tokens with 7-day session persistence |
| **Web Scraping / Sanitization** | **BeautifulSoup4** | `^4.12.0` | Strips tags, scripts, and normalizes block-level whitespace |
| **Test Suite** | **pytest**, **httpx** | `^9.0.0` | 72 isolated in-memory automated unit and e2e integration tests |
| **Frontend Framework** | **React** | `^18.3.1` | Declarative component UI library |
| **Build Tool & Dev Server**| **Vite** | `^6.0.0` | Instant HMR and high-speed ES-module bundler |
| **Styling** | **Tailwind CSS** | `^4.0.0` | Modern utility-first CSS via `@tailwindcss/vite` |
| **Routing** | **React Router** | `^6.28.0` | Client-side routing with authentication guards |
| **HTTP Client** | **Axios** | `^1.7.9` | Request/response interceptors with JWT injection & 75s cold-start timeout |
| **Icons** | **Lucide React** | `^0.475.0` | Accessible, consistent iconography |

---

## 📁 Project Structure

```text
e:\Skill Analyzer\
├── backend/
│   ├── app/
│   │   ├── connectors/             # Pluggable ATS source connectors
│   │   │   ├── base.py             # NormalizedJob model & BaseJobConnector interface
│   │   │   ├── greenhouse.py       # Greenhouse public board API connector
│   │   │   └── lever.py            # Lever public board API connector
│   │   ├── models/                 # SQLAlchemy relational ORM models
│   │   │   ├── user.py             # Users table with Argon2 hashes & relationships
│   │   │   ├── student_profile.py  # Student profile (degree, graduation, bio, mobile, avatar)
│   │   │   ├── password_reset.py   # Secure single-use hashed reset tokens
│   │   │   ├── analysis.py         # Analyses table (employer, role, study hours)
│   │   │   ├── student_skill.py    # Self-reported student skills & proficiency
│   │   │   ├── job_snapshot.py     # Verified posting snapshots, hashes & URLs
│   │   │   ├── required_skill.py   # Extracted skills with sentence evidence quotes
│   │   │   └── roadmap_item.py     # Generated weekly curriculum items & status
│   │   ├── resources/              # Free educational catalog & role benchmarks
│   │   │   ├── learning_resources.json  # Curated catalog with verified free URLs
│   │   │   ├── archived_job_snapshots.json # Verified historical postings archive (Approach 1)
│   │   │   └── industry_role_benchmarks.json # Standard technical competency frameworks (Approach 2)
│   │   ├── routes/                 # FastAPI API route controllers
│   │   │   ├── health.py           # /api/health with database probe
│   │   │   ├── auth.py             # /api/auth/register, login, me, forgot/reset-password
│   │   │   ├── profile.py          # GET/PUT /api/profile student profile endpoints
│   │   │   ├── analyses.py         # CRUD analyses, job search, gap analysis
│   │   │   └── roadmap.py          # GET/POST /api/analyses/{id}/roadmap, PATCH item
│   │   ├── schemas/                # Pydantic v2 validation models
│   │   │   ├── profile.py          # Student profile view/update schemas
│   │   │   ├── password_reset.py   # Forgot/reset password request schemas
│   │   │   └── analysis.py         # Analysis requests with IT domain role validator
│   │   ├── security/               # Password hashing, JWT creation & auth dependencies
│   │   ├── services/               # Core business logic engines
│   │   │   ├── role_validator.py   # IT role domain classifier, non-IT rejection & typo tolerance
│   │   │   ├── email_service.py    # SMTP email sender with dev console fallback
│   │   │   ├── skill_normalizer.py # Canonical alias normalizer
│   │   │   ├── job_search_service.py # Multi-source aggregation & freshness
│   │   │   ├── skill_extractor.py  # Regex disambiguation & evidence extractor
│   │   │   ├── gap_analyzer.py     # Gap categorization & coverage metric
│   │   │   └── roadmap_generator.py# Budget-bounded priority weekly scheduler
│   │   ├── config.py               # Pydantic BaseSettings loading from .env (auto-normalizes postgres://)
│   │   ├── database.py             # SQLAlchemy engine with pool_pre_ping & connection recycling
│   │   └── main.py                 # FastAPI application factory, CORS & route registration
│   ├── tests/                      # Automated test suite (72 passing tests)
│   │   ├── conftest.py             # In-memory SQLite fixtures & TestClient
│   │   ├── test_health.py          # Health-check probe tests (2 tests)
│   │   ├── test_auth.py            # Registration, login, JWT validation tests (9 tests)
│   │   ├── test_profile.py         # Student profile GET/PUT and auth isolation tests (4 tests)
│   │   ├── test_password_reset.py  # Forgot password, token hashing & reset tests (4 tests)
│   │   ├── test_analyses.py        # Analysis CRUD, ownership scoping tests (7 tests)
│   │   ├── test_connectors.py      # Greenhouse ATS integration & cleaning tests (5 tests)
│   │   ├── test_lever_and_aggregation.py # Lever ATS & multi-source dedup tests (10 tests)
│   │   ├── test_skill_extraction_and_gap.py # Skill regex disambiguation & gap tests (11 tests)
│   │   ├── test_roadmap.py         # Weekly hour budget & curriculum tests (5 tests)
│   │   ├── test_cached_snapshots.py # Snapshots, benchmarks & role rejection tests (14 tests)
│   │   └── test_e2e_workflow.py    # Comprehensive full-student journey e2e test (1 test)
│   ├── .env.example                # Backend configuration template
│   ├── pytest.ini                  # Pytest configuration & warning filters
│   └── requirements.txt            # Python dependencies (includes psycopg2-binary)
├── frontend/
│   ├── src/
│   │   ├── api/                    # Axios instances & endpoint services
│   │   │   ├── axios.js            # Axios client with 75s timeout & bearer interceptor
│   │   │   ├── auth.js             # Auth, forgot-password & reset-password endpoints
│   │   │   ├── profile.js          # Profile GET/PUT endpoints
│   │   │   ├── analyses.js         # Analyses & job search endpoints
│   │   │   └── roadmap.js          # Roadmap & progress tracking endpoints
│   │   ├── components/             # Reusable UI components
│   │   │   ├── Navbar.jsx          # Header navigation with profile link & avatar badge
│   │   │   ├── ProtectedRoute.jsx  # Auth guard routing wrapper
│   │   │   ├── SkillCard.jsx       # Evidence-backed requirement card
│   │   │   ├── JobSourceCard.jsx   # Verified job source card with link & badge
│   │   │   ├── SkillGapChart.jsx   # Visual breakdown of coverage metric
│   │   │   ├── LoadingState.jsx    # Animated loading spinner with message
│   │   │   └── ErrorState.jsx      # Error banner with retry trigger
│   │   ├── context/
│   │   │   └── AuthContext.jsx     # User state provider & resilient session persistence
│   │   ├── pages/                  # Top-level view routes
│   │   │   ├── Login.jsx           # Student login with Render warm-up banner & reset alerts
│   │   │   ├── Register.jsx        # Student registration screen
│   │   │   ├── ForgotPassword.jsx  # Password reset request screen
│   │   │   ├── ResetPassword.jsx   # Secure token-based password reset screen
│   │   │   ├── Profile.jsx         # Student profile management UI (avatars, bio, academics)
│   │   │   ├── Dashboard.jsx       # Student analyses portfolio & creation link
│   │   │   ├── NewAnalysis.jsx     # Free-text form for employer, role & skills
│   │   │   ├── AnalysisResult.jsx  # Verified jobs, evidence quotes & gap results
│   │   │   ├── Roadmap.jsx         # Week-by-week curriculum & progress checkboxes
│   │   │   └── NotFound.jsx        # Friendly 404 page
│   │   ├── App.jsx                 # Route definitions & router setup
│   │   ├── index.css               # Tailwind CSS v4 entry point
│   │   └── main.jsx                # React DOM mount point
│   ├── .env.example                # Frontend environment template
│   ├── package.json                # Node dependencies & build scripts
│   ├── vite.config.js              # Vite configuration with React & Tailwind plugins
│   └── index.html                  # HTML entry point
├── .gitignore                      # Git ignore rules
└── README.md                       # Complete project documentation
```

---

## 🚀 Local Development Setup (Windows PowerShell)

Follow these step-by-step commands to run the backend and frontend simultaneously in separate PowerShell windows.

### 1. Backend Setup

Open **Terminal 1** (Windows PowerShell) in the repository root:

```powershell
# 1. Navigate into backend directory
cd "e:\Skill Analyzer\backend"

# 2. Create Python virtual environment
py -m venv venv

# 3. Activate virtual environment
.\venv\Scripts\Activate.ps1

# (Optional: If PowerShell restricts scripts, execute):
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# 4. Upgrade pip and install all dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 5. Create local development .env (if not present)
Copy-Item .env.example .env

# 6. Start the FastAPI development server with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Backend Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### 2. Frontend Setup

Open **Terminal 2** (Windows PowerShell) in the repository root:

```powershell
# 1. Navigate into frontend directory
cd "e:\Skill Analyzer\frontend"

# 2. Install Node dependencies
npm install

# 3. Create local development .env
Copy-Item .env.example .env

# 4. Start the Vite development server
npm run dev
```

- **Frontend Application URL**: [http://localhost:5173](http://localhost:5173)

---

## 🧪 Automated Test Suite

The test suite runs **72 automated tests** in an isolated, in-memory SQLite database environment without affecting your local database.

In **Terminal 1** (with virtual environment activated):

```powershell
# From the repository root or backend directory:
pytest -v -c backend/pytest.ini backend/tests
```

### Verified Test Suite Breakdown (72 Passing Tests)

```text
backend/tests/test_health.py (2 tests)
  ✓ test_health_check_returns_ok_with_database_connected
  ✓ test_health_check_database_unhealthy

backend/tests/test_auth.py (9 tests)
  ✓ test_register_success
  ✓ test_register_duplicate_email
  ✓ test_register_weak_password
  ✓ test_register_invalid_email
  ✓ test_login_success
  ✓ test_login_wrong_password
  ✓ test_login_nonexistent_email
  ✓ test_get_me_authenticated
  ✓ test_get_me_unauthorized

backend/tests/test_profile.py (4 tests)
  ✓ test_get_profile_auto_initializes_empty_profile
  ✓ test_update_profile_success
  ✓ test_update_profile_validation_errors
  ✓ test_profile_requires_authentication

backend/tests/test_password_reset.py (4 tests)
  ✓ test_forgot_password_always_returns_neutral_success
  ✓ test_reset_password_success
  ✓ test_reset_password_invalid_or_expired_token
  ✓ test_reset_password_mismatched_confirmation

backend/tests/test_analyses.py (7 tests)
  ✓ test_create_analysis_success
  ✓ test_create_analysis_invalid_hours
  ✓ test_list_analyses_user_scoped
  ✓ test_get_analysis_by_id_owner
  ✓ test_get_analysis_by_id_idor_prevented
  ✓ test_delete_analysis_cascades
  ✓ test_delete_analysis_idor_prevented

backend/tests/test_connectors.py (5 tests)
  ✓ test_greenhouse_connector_success
  ✓ test_greenhouse_connector_company_not_found
  ✓ test_greenhouse_token_relevance_filter
  ✓ test_html_sanitizer_cleans_tags_and_whitespace
  ✓ test_token_relevance_scorer_boundary_conditions

backend/tests/test_lever_and_aggregation.py (10 tests)
  ✓ test_lever_connector_success
  ✓ test_lever_connector_company_not_found
  ✓ test_lever_token_relevance_filter
  ✓ test_aggregation_combines_sources
  ✓ test_aggregation_deduplicates_identical_roles
  ✓ test_aggregation_freshness_policy
  ✓ test_aggregation_company_not_verified_status
  ✓ test_aggregation_source_unavailable_status
  ✓ test_aggregation_no_matching_jobs_status
  ✓ test_api_search_jobs_flow

backend/tests/test_skill_extraction_and_gap.py (11 tests)
  ✓ test_extract_skills_from_posting
  ✓ test_disambiguation_c_plus_plus_and_c_sharp
  ✓ test_disambiguation_r_and_go
  ✓ test_requirement_level_classification
  ✓ test_gap_analysis_calculates_coverage
  ✓ test_gap_analysis_missing_skills
  ✓ test_gap_analysis_needs_improvement
  ✓ test_gap_analysis_additional_skills
  ✓ test_gap_analysis_zero_required_skills_guard
  ✓ test_api_run_gap_analysis_flow
  ✓ test_api_run_gap_analysis_requires_verified_jobs

backend/tests/test_roadmap.py (5 tests)
  ✓ test_generate_roadmap_budget_bounded
  ✓ test_roadmap_prioritizes_missing_required_skills
  ✓ test_api_generate_and_fetch_roadmap_flow
  ✓ test_api_update_roadmap_item_status
  ✓ test_roadmap_requires_analysis_owner

backend/tests/test_cached_snapshots.py (14 tests)
  ✓ test_find_cached_snapshots_from_catalog
  ✓ test_find_cached_snapshots_from_database_precedence
  ✓ test_apply_cached_snapshot_to_analysis
  ✓ test_api_use_cached_posting_and_run_gap_analysis
  ✓ test_find_cached_snapshots_for_hcltech_and_alias
  ✓ test_api_paste_job_description_flow
  ✓ test_find_industry_role_benchmark
  ✓ test_apply_industry_benchmark_to_analysis
  ✓ test_api_use_industry_benchmark_flow
  ✓ test_find_cached_snapshots_deloitte_and_mastercard
  ✓ test_typo_tolerant_role_matching
  ✓ test_disjunctive_programming_language_alternative_handling
  ✓ test_unregistered_company_produces_no_generic_skills
  ✓ test_invalid_and_non_it_job_roles_rejected

backend/tests/test_e2e_workflow.py (1 test)
  ✓ test_full_student_e2e_journey (Complete end-to-end integration lifecycle)
```

---

## 📡 REST API Reference

All protected endpoints require an `Authorization: Bearer <token>` header.

### Authentication Endpoints

#### `POST /api/auth/register`
- **Auth**: None
- **Payload**:
  ```json
  {
    "name": "Sarah Student",
    "email": "sarah.student@university.edu",
    "password": "SecurePassword123!"
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "name": "Sarah Student",
      "email": "sarah.student@university.edu",
      "created_at": "2026-10-25T12:00:00Z"
    }
  }
  ```

#### `POST /api/auth/login`
- **Auth**: None
- **Payload**:
  ```json
  {
    "email": "sarah.student@university.edu",
    "password": "SecurePassword123!"
  }
  ```
- **Response**: `200 OK` (Returns same JWT structure as register)

#### `GET /api/auth/me`
- **Auth**: Bearer Token
- **Response**: `200 OK` (Current student profile, never returning password hash)

#### `POST /api/auth/forgot-password`
- **Auth**: None
- **Payload**:
  ```json
  {
    "email": "sarah.student@university.edu"
  }
  ```
- **Action**: Generates a cryptographically random, single-use reset token valid for 15 minutes. The token is hashed with SHA-256 before storing in the database. Dispatches an email via SMTP (or prints to server logs in local dev). Returns a neutral message to prevent user enumeration attacks.
- **Response**: `200 OK`
  ```json
  {
    "message": "If an account exists with this email address, a password reset link has been sent."
  }
  ```

#### `POST /api/auth/reset-password`
- **Auth**: None
- **Payload**:
  ```json
  {
    "token": "48_char_secure_random_hex_token",
    "new_password": "NewSecurePassword456!",
    "confirm_password": "NewSecurePassword456!"
  }
  ```
- **Action**: Validates token existence, expiration, and unused status. Re-hashes the new password with Argon2id, invalidates the token, and updates the user account.
- **Response**: `200 OK`
  ```json
  {
    "message": "Password has been successfully reset. You may now log in with your new password."
  }
  ```

---

### Student Profile Endpoints

#### `GET /api/profile`
- **Auth**: Bearer Token
- **Action**: Retrieves the authenticated student's profile details. Automatically initializes an empty profile on first visit.
- **Response**: `200 OK`
  ```json
  {
    "id": 1,
    "user_id": 1,
    "email": "sarah.student@university.edu",
    "name": "Sarah Student",
    "mobile_number": "+1 555-0199",
    "college_name": "University of Technology",
    "degree": "Bachelor of Technology (B.Tech)",
    "specialization": "Computer Science & Engineering",
    "graduation_year": 2027,
    "study_hours_per_week": 15,
    "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=Sarah",
    "bio": "Aspiring Cloud Backend Engineer passionate about distributed systems.",
    "skills": ["Python", "Docker", "PostgreSQL"],
    "created_at": "2026-10-25T12:00:00Z",
    "updated_at": "2026-10-26T14:30:00Z"
  }
  ```

#### `PUT /api/profile`
- **Auth**: Bearer Token
- **Action**: Updates the student profile fields (email is read-only). Enforces graduation year range (1970–2040), max 100 study hours/week, and max 50 skills.
- **Response**: `200 OK` (Returns updated profile JSON)

---

### Analysis Endpoints

#### `POST /api/analyses`
- **Auth**: Bearer Token
- **Payload**:
  ```json
  {
    "company_name": "Stripe",
    "target_role": "Backend Engineer",
    "weekly_hours": 10,
    "student_skills": [
      { "name": "Python", "proficiency": "intermediate" },
      { "name": "Git", "proficiency": "beginner" }
    ]
  }
  ```
- **Validation**: Enforces IT & technology domain role validation (`validate_it_role`). Rejects non-IT professions (e.g. `Civil Engineer`, `Medical Doctor`, `Accountant`) and nonsensical inputs (e.g. `Quantum Banana Analyst 987654`) with HTTP 422:
  `"This job role is invalid or is not currently supported by our IT and technology job analysis system. Please enter a valid IT or technology-related job role."`
  Accepts arbitrary valid free-text tech titles (e.g., `Site Reliability Engineer`, `Full Stack Developer`, `Junior Systems Apprentice`) with typo-tolerant matching (e.g., `Anaylst`).
- **Response**: `201 Created` with initialized analysis entity (`status: "pending"`).

#### `GET /api/analyses`
- **Auth**: Bearer Token
- **Response**: `200 OK` (List of student's analyses scoped by user ID with skill counts and job counts).

#### `GET /api/analyses/{id}`
- **Auth**: Bearer Token (Owner only; returns 404 for IDOR security if accessed by another user)
- **Response**: `200 OK` (Analysis details including self-reported skills and verified job snapshots).

#### `DELETE /api/analyses/{id}`
- **Auth**: Bearer Token (Owner only)
- **Response**: `204 No Content` (Cascades deletion to student skills, snapshots, extracted requirements, and roadmap items).

#### `POST /api/analyses/{id}/search-jobs`
- **Auth**: Bearer Token
- **Action**: Queries configured ATS connectors (Greenhouse, Lever) in priority sequence. Normalizes postings, applies token relevance filters, checks posting freshness against `JOB_FRESHNESS_DAYS = 30`, and stores deduplicated snapshots in SQLite.
- **Response**: `200 OK` with `status: "verified_jobs_found"` or honest fallbacks (`company_not_verified`, `no_matching_jobs`, `source_unavailable`). If no live jobs are found, returns `has_cached_snapshots: true` when a verified historical posting is available.

#### `POST /api/analyses/{id}/use-cached-posting` (Approach 1)
- **Auth**: Bearer Token (Owner only)
- **Action**: Attaches the most recent verified historical snapshot (from the local database cache or verified archive catalog) to the analysis when live feeds have no open listings. Marks the snapshot with `is_stale: true`, `verification_status: "archived_snapshot"`, and an explicit provenance note.
- **Response**: `200 OK` with `status: "archived_jobs_found"`, allowing immediate evidence-backed gap analysis and roadmap generation.

#### `POST /api/analyses/{id}/use-industry-benchmark` (Approach 2)
- **Auth**: Bearer Token (Owner only)
- **Action**: Instant 1-click fallback applying a verified industry competency benchmark (e.g. ISO/Standard Software Engineer, Data Analyst, DevOps) when the target company (e.g., Lemma, RBIS, TCS) does not publish an open public ATS feed.
- **Response**: `200 OK` with `status: "verified_jobs_found"`, setting `verification_status: "industry_benchmark"`, ready for instant gap analysis.

#### `POST /api/analyses/{id}/paste-job-description`
- **Auth**: Bearer Token (Owner only)
- **Payload**:
  ```json
  {
    "description_text": "Required: 2+ years of Java, Spring Boot, and PostgreSQL...",
    "job_title": "Java Developer",
    "source_url": "https://company.com/careers/java-dev"
  }
  ```
- **Action**: Ingests direct student-provided job descriptions (e.g., copied from LinkedIn, Naukri, or enterprise portals), cleaning HTML and generating a `user_provided_posting` snapshot with honest student provenance.
- **Response**: `200 OK` with `status: "verified_jobs_found"`.

#### `POST /api/analyses/{id}/run-gap-analysis`
- **Auth**: Bearer Token
- **Action**: Runs contextual regex disambiguation over verified posting text. Quotes exact supporting sentences, classifies requirement priority, compares against self-reported student skills, and calculates the coverage percentage.
- **Response**: `200 OK`
  ```json
  {
    "analysis_id": 1,
    "target_role": "Backend Engineer",
    "company_name": "Stripe",
    "total_verified_jobs": 2,
    "coverage_percentage": 25.0,
    "coverage_explanation": "Coverage reflects that 1 of 4 verified required technical skills is self-reported as covered.",
    "skill_gaps": [
      {
        "skill_name": "Python",
        "requirement_type": "required",
        "evidence_quote": "Required: 3+ years experience with Python and Docker.",
        "student_proficiency": "intermediate",
        "gap_category": "self_reported_covered",
        "is_covered": true
      },
      {
        "skill_name": "Docker",
        "requirement_type": "required",
        "evidence_quote": "Required: 3+ years experience with Python and Docker.",
        "student_proficiency": "missing",
        "gap_category": "missing",
        "is_covered": false
      }
    ],
    "additional_skills": []
  }
  ```

---

### Personalized Roadmap Endpoints

#### `POST /api/analyses/{id}/roadmap`
- **Auth**: Bearer Token
- **Action**: Synthesizes a rules-based, time-bounded curriculum mapping verified skill gaps to verified free educational resources.
- **Response**: `201 Created`
  ```json
  {
    "analysis_id": 1,
    "target_role": "Backend Engineer",
    "company_name": "Stripe",
    "weekly_hours_budget": 10,
    "total_weeks": 4,
    "total_estimated_hours": 32,
    "items": [
      {
        "id": 1,
        "week_number": 1,
        "skill_name": "Docker",
        "topic": "Containers & Virtualization",
        "resource_title": "Docker Official Getting Started Guide",
        "resource_url": "https://docs.docker.com/get-started/",
        "resource_provider": "Docker Docs",
        "estimated_hours": 6,
        "status": "not_started"
      }
    ]
  }
  ```

#### `GET /api/analyses/{id}/roadmap`
- **Auth**: Bearer Token
- **Response**: `200 OK` (Fetches current roadmap items and progress).

#### `PATCH /api/roadmap-items/{id}`
- **Auth**: Bearer Token (Owner only)
- **Payload**: `{ "status": "in_progress" }` (or `completed`, `not_started`)
- **Response**: `200 OK`

---

## ⚙️ Engine & Algorithm Specifications

### 1. Explainable Token Relevance

When searching career feeds with hundreds of open requisitions, naive keyword searches cause severe false positives (e.g. matching an *Account Executive* for a *Senior Backend Engineer* query).
Our relevance engine calculates token and phrase overlap:

1. **Stemming & Stopword Removal**: Removes non-informative tokens (`the`, `and`, `engineer`, `developer`, `senior`, `staff`, `lead`).
2. **Exact Phrase Matching**: If target role keywords appear as a contiguous substring in the job title, returns `relevance = 1.0`.
3. **Jaccard Token Overlap**: Computes $\frac{|T_{\text{role}} \cap T_{\text{job}}|}{|T_{\text{role}}|}$.
4. **Threshold Guard**: Only postings with relevance score $\ge 0.5$ are saved as verified snapshots.

---

### 2. Disambiguated Evidence Extraction

Extracting technical skills with regex presents severe risk of false positives on single/short symbols (e.g. `R` matching every letter 'r', `C` matching every word starting with 'c', `Go` matching the English verb "go").
Our engine uses multi-stage disambiguation:

- **Multi-Word Longest-First Matching**: Multi-word phrases like `Machine Learning`, `PostgreSQL`, `Spring Boot` are processed before individual tokens.
- **Contextual Boundary Regex**:
  - `C++`: `\b[cC]\+\+(?!\w)` (prevents `\b` failure on `+`).
  - `C#`: `\b[cC]#(?!\w)` (prevents `\b` failure on `#`).
  - `R`: Matches only when preceded/followed by language context like `\b[rR]\s+(?:programming|scripting|language)\b` or `\b(?:in|using)\s+[rR]\b`.
  - `Go`: Matches only when disambiguated as `\b(?:Golang|Go\s+language|Go\s+programming)\b` or alongside other programming terms.
- **Requirement Priority Classification**:
  Contextual sentence windows are scanned for indicative phrasing:
  - `preferred`: `"is a plus"`, `"preferred"`, `"nice to have"`, `"bonus"`, `"optional"`.
  - `required`: `"required"`, `"must have"`, `"qualifications"`, `"minimum"`, `"years experience"`.
  - `mentioned`: Default fallback when context is neutral.

---

### 3. Skill-Gap Categorization & Coverage Formula

Each verified requirement is compared against self-reported student proficiency:

| Student Level | Requirement Level | Assigned Gap Category | Is Covered |
| :--- | :--- | :--- | :---: |
| Not reported | Any | `missing` | ❌ |
| `beginner` | `required` | `needs_improvement` | ❌ |
| `beginner` | `preferred` / `mentioned` | `self_reported_covered` | ✅ |
| `intermediate` / `advanced` | Any | `self_reported_covered` | ✅ |
| Reported by student | Not in verified job | `additional_skill` | N/A |

#### Coverage Metric Formula:
$$\text{Coverage} = \left( \frac{\text{Count of strictly required skills marked } \texttt{self\_reported\_covered}}{\text{Total count of verified strictly required skills}} \right) \times 100$$

- **Denominator Guard**: Only skills classified as `required` are counted in the denominator.
- **Honest Null**: If 0 required skills are found, returns `null` with explanation *"Not enough verified data"*, never a false 0%.

---

### 4. Weekly Budget-Constrained Roadmap Scheduling

A common defect in learning roadmaps is overloading students with unrealistic schedules. Our engine enforces the student's declared `weekly_hours` budget:

1. **Ordering Hierarchy**:
   1. `missing` required skills (highest priority).
   2. `needs_improvement` required skills.
   3. `missing` preferred skills.
2. **Weekly Packing Algorithm**:
   - Items are allocated into `week_number = 1`.
   - If adding a topic's estimated hours would cause $\sum \text{hours}_{\text{week}} > \text{weekly\_hours}$, the item automatically rolls over into `week_number + 1`.
   - Extended across as many weeks as needed rather than compressing into unrealistic workloads.

---

### 5. IT Domain Role Validation & Typo Tolerance

To maintain domain accuracy and prevent nonsensical IT skill extraction for non-IT occupations, the system includes an IT domain role validator (`app/services/role_validator.py`):

1. **Non-IT Profession Filtering**:
   Explicitly checks against known non-IT occupations (e.g., `Civil Engineer`, `Medical Doctor`, `Registered Nurse`, `Accountant`, `Electrician`, `Chef`, `Lawyer`, `Pilot`).
2. **Nonsense & Gibberish Filtering**:
   Rejects inputs containing nonsense words (e.g., `banana`, `quantum banana`), random digit sequences (e.g., `987654`), or excessive non-alphanumeric characters.
3. **Free-Text IT Domain Matcher**:
   Rather than restricting students to a small hardcoded drop-down, the engine allows arbitrary free-text tech titles (e.g. `Site Reliability Engineer`, `Full Stack Developer`, `Junior Systems Apprentice`, `Cloud Architect`, `DevOps Specialist`).
4. **Typo Tolerance**:
   Incorporates normalized edit-distance matching (Levenshtein/difflib ratio $\ge 0.8$) so common student typos (e.g., `Anaylst`, `Develper`) are recognized as valid tech roles.
5. **Exact Rejection Specification**:
   When an invalid or non-IT role is entered, the API immediately halts with HTTP 422:
   > *"This job role is invalid or is not currently supported by our IT and technology job analysis system. Please enter a valid IT or technology-related job role."*

---

## 🔌 Extensibility Guide

### Adding a New Permitted Job Connector

All connectors inherit from `BaseJobConnector` in `backend/app/connectors/base.py`:

```python
from app.connectors.base import BaseJobConnector, NormalizedJob

class AshbyConnector(BaseJobConnector):
    source_name = "Ashby"
    source_type = "public_ats_feed"

    def search_jobs(self, company_name: str, target_role: str) -> list[NormalizedJob]:
        # 1. Fetch public jobs feed for company
        # 2. Clean HTML with clean_html_description()
        # 3. Filter by calculate_role_relevance()
        # 4. Return list of NormalizedJob instances
        ...
```

Then register the new connector in `backend/app/services/job_search_service.py`:

```python
def get_default_connectors() -> list[BaseJobConnector]:
    return [
        GreenhouseConnector(),
        LeverConnector(),
        AshbyConnector(),  # Added here
    ]
```

---

### Adding New Curated Learning Resources

The learning catalog is stored in `backend/app/resources/learning_resources.json`. To add resources:

```json
{
  "skill_name": "Kubernetes",
  "topic": "Container Orchestration",
  "title": "Kubernetes Official Tutorials",
  "url": "https://kubernetes.io/docs/tutorials/",
  "provider": "Kubernetes.io",
  "access_status": "free",
  "estimated_hours": 8,
  "level": "intermediate",
  "description": "Hands-on interactive exercises deploying pods, deployments, and services."
}
```

Every resource MUST be genuinely free, without paywalls or hidden trial credit requirements.

---

## 🛡️ Limitations, Privacy & Ethical Compliance

1. **Rate Limits & Source Feeds**:
   The application queries permitted, publicly accessible career feeds (e.g. Greenhouse public board API, Lever careers API). It complies with rate limits, headers, and robots.txt policies.
2. **No Storage of Full Job Postings**:
   To respect copyright and terms of service, the system stores normalized excerpts and sentence-level evidence strings rather than republishing or redistributing complete proprietary job descriptions.
3. **Extraction Limitations**:
   Regex and rule-based extraction provide explainable evidence tracing without non-deterministic LLM hallucinations. However, unusual phrasing or novel slang may not match the taxonomy. The catalog is continuously expandable.
4. **Guidepost Disclaimer**:
   Effort estimates (hours per topic) and the skill coverage metric are illustrative educational guidelines designed for self-study planning. They do not constitute a formal accreditation or hiring guarantee.

---

## ☁️ Production Deployment & Database Persistence (Render Free Tier)

When deploying on Render's free tier, understanding container lifecycle and data persistence is critical to prevent user accounts from disappearing.

### Root Cause of Missing Accounts on Render Free Tier

Render Web Services run inside **ephemeral Docker containers**:
1. When a free web service receives no traffic for 15 minutes, Render spins down the container to 0 instances.
2. When a new request arrives, Render spins up a **brand-new container** with a fresh file system.
3. If SQLite (`sqlite:///./app.db`) is used on a Web Service without a persistent disk, **the database file is wiped on every spin-down or redeploy**.
4. Consequently, any student accounts registered on the previous container instance vanish, and subsequent logins fail.

### Solution: Free Render PostgreSQL Database

Render provides a free managed PostgreSQL database with persistent storage that survives container restarts.

#### Step 1: Create a PostgreSQL Instance on Render
1. Log in to the [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **PostgreSQL**.
3. Set a name (e.g., `skill-analyzer-db`) and select the **Free** tier.
4. Click **Create Database**.

#### Step 2: Configure Environment Variables in the Web Service
1. In your Render PostgreSQL dashboard, copy the **Internal Database URL** (e.g., `postgres://user:password@dpg-xxx:5432/dbname`).
2. Go to your **Backend Web Service** settings on Render > **Environment**.
3. Add or update the following environment variables:

| Variable | Recommended Value | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgres://user:pass@dpg-xxx:5432/dbname` | Render Internal Database URL. The backend automatically normalizes `postgres://` to `postgresql://` and configures connection pooling (`pool_pre_ping=True`, `pool_recycle=300`). |
| `JWT_SECRET` | *(64-character random string)* | Strong cryptographic secret for signing bearer tokens. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | Sets JWT session validity to 7 days, preventing premature student logouts. |
| `FRONTEND_ORIGIN` | `https://your-frontend.onrender.com` | Allowed CORS origin for the React SPA. |
| `SMTP_HOST` | *(Optional, e.g., `smtp.gmail.com`)* | Host for outgoing password reset emails. |
| `SMTP_PORT` | `587` | Port for TLS email dispatch. |
| `SMTP_USER` | *(Optional, e.g., `your-email@gmail.com`)* | SMTP authentication email. |
| `SMTP_PASSWORD` | *(Optional, e.g., Google App Password)* | SMTP application password. |
| `SMTP_FROM_EMAIL` | `noreply@skillanalyzer.dev` | From header for password reset emails. |

> [!NOTE]
> If SMTP credentials are not configured, password reset tokens are safely logged to the backend service stdout/console logs for convenient testing.

#### Step 3: Frontend Cold-Start Protection
Render free web services spin down after inactivity and take 30–50 seconds to warm up on the first request. The frontend includes:
- An increased Axios timeout of **75 seconds** (`frontend/src/api/axios.js`), preventing premature request abortion.
- A dynamic warm-up banner on the Login screen informing students if the server takes longer than 4 seconds to respond.
- Resilient auth initialization in `AuthContext.jsx` that preserves local credentials during transient connection timeouts.

---

## 📄 License

This project is licensed under the **MIT License**. Free and open-source for personal and educational use.
