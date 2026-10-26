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
9. [Extensibility Guide](#-extensibility-guide)
   - [Adding a New Permitted Source Connector](#adding-a-new-permitted-job-connector)
   - [Adding New Curated Learning Resources](#adding-new-curated-learning-resources)
10. [Limitations, Privacy & Ethical Compliance](#-limitations-privacy--ethical-compliance)

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
| **Database & ORM** | **SQLAlchemy** + **SQLite** | `^2.0.0` | Relational models, cascade foreign keys, local persistence |
| **Password Security** | **Argon2id** (`pwdlib`) | `^0.2.0` | Modern, GPU-resistant memory-hard password hashing |
| **Authentication** | **PyJWT** | `^2.10.0` | Stateless HMAC-SHA256 bearer tokens with 30m expiry |
| **Web Scraping / Sanitization** | **BeautifulSoup4** | `^4.12.0` | Strips tags, scripts, and normalizes block-level whitespace |
| **Test Suite** | **pytest**, **httpx** | `^9.0.0` | 58 isolated in-memory automated unit and e2e integration tests |
| **Frontend Framework** | **React** | `^18.3.1` | Declarative component UI library |
| **Build Tool & Dev Server**| **Vite** | `^6.0.0` | Instant HMR and high-speed ES-module bundler |
| **Styling** | **Tailwind CSS** | `^4.0.0` | Modern utility-first CSS via `@tailwindcss/vite` |
| **Routing** | **React Router** | `^6.28.0` | Client-side routing with authentication guards |
| **HTTP Client** | **Axios** | `^1.7.9` | Request/response interceptors with automatic JWT injection |
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
│   │   │   ├── user.py             # Users table with Argon2 hashes
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
│   │   │   ├── health.py           # /api/health with SELECT 1 SQLite probe
│   │   │   ├── auth.py             # /api/auth/register, login, me
│   │   │   ├── analyses.py         # CRUD analyses, job search, gap analysis
│   │   │   └── roadmap.py          # GET/POST /api/analyses/{id}/roadmap, PATCH item
│   │   ├── schemas/                # Pydantic v2 validation models
│   │   ├── security/               # Password hashing, JWT creation & auth dependencies
│   │   ├── services/               # Core business logic engines
│   │   │   ├── skill_normalizer.py # Canonical alias normalizer
│   │   │   ├── job_search_service.py # Multi-source aggregation & freshness
│   │   │   ├── skill_extractor.py  # Regex disambiguation & evidence extractor
│   │   │   ├── gap_analyzer.py     # Gap categorization & coverage metric
│   │   │   └── roadmap_generator.py# Budget-bounded priority weekly scheduler
│   │   ├── config.py               # Pydantic BaseSettings loading from .env
│   │   ├── database.py             # SQLite engine & session maker
│   │   └── main.py                 # FastAPI application factory & CORS setup
│   ├── tests/                      # Automated test suite (58 passing tests)
│   │   ├── conftest.py             # In-memory SQLite fixtures & TestClient
│   │   ├── test_health.py          # Health-check probe tests
│   │   ├── test_auth.py            # Registration, login, JWT validation tests
│   │   ├── test_analyses.py        # Analysis CRUD, ownership scoping tests
│   │   ├── test_connectors.py      # Greenhouse ATS integration & cleaning tests
│   │   ├── test_lever_and_aggregation.py # Lever ATS & multi-source dedup tests
│   │   ├── test_skill_extraction_and_gap.py # Skill regex disambiguation & gap tests
│   │   ├── test_roadmap.py         # Weekly hour budget & curriculum tests
│   │   ├── test_e2e_workflow.py    # Comprehensive full-student journey e2e test
│   │   └── test_cached_snapshots.py # Cached snapshots, benchmarks & paste flow tests (9 tests)
│   ├── .env.example                # Backend configuration template
│   ├── pytest.ini                  # Pytest configuration & warning filters
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/                    # Axios instances & endpoint services
│   │   │   ├── axios.js            # Axios client with bearer token interceptor
│   │   │   ├── auth.js             # Auth endpoints
│   │   │   ├── analyses.js         # Analyses & job search endpoints
│   │   │   └── roadmap.js          # Roadmap & progress tracking endpoints
│   │   ├── components/             # Reusable UI components
│   │   │   ├── Navbar.jsx          # Header navigation with user status & logout
│   │   │   ├── ProtectedRoute.jsx  # Auth guard routing wrapper
│   │   │   ├── SkillCard.jsx       # Evidence-backed requirement card
│   │   │   ├── JobSourceCard.jsx   # Verified job source card with link & badge
│   │   │   ├── SkillGapChart.jsx   # Visual breakdown of coverage metric
│   │   │   ├── LoadingState.jsx    # Animated loading spinner with message
│   │   │   └── ErrorState.jsx      # Error banner with retry trigger
│   │   ├── context/
│   │   │   └── AuthContext.jsx     # User state provider & session persistence
│   │   ├── pages/                  # Top-level view routes
│   │   │   ├── Login.jsx           # Student login screen
│   │   │   ├── Register.jsx        # Student registration screen
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

The test suite runs 49 automated tests in an isolated, in-memory SQLite database environment without affecting your local database.

In **Terminal 1** (with virtual environment activated):

```powershell
# From the repository root or backend directory:
pytest -v -c backend/pytest.ini backend/tests
```

### Verified Test Suite Breakdown (58 Passing Tests)

```text
backend/tests/test_analyses.py (7 tests)
...
backend/tests/test_cached_snapshots.py (9 tests)
  ✓ test_find_cached_snapshots_from_catalog
  ✓ test_find_cached_snapshots_from_database_precedence
  ✓ test_apply_cached_snapshot_to_analysis
  ✓ test_api_use_cached_posting_and_run_gap_analysis
  ✓ test_find_cached_snapshots_for_hcltech_and_alias
  ✓ test_api_paste_job_description_flow
  ✓ test_find_industry_role_benchmark
  ✓ test_apply_industry_benchmark_to_analysis
  ✓ test_api_use_industry_benchmark_flow
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

## 📄 License

This project is licensed under the **MIT License**. Free and open-source for personal and educational use.
