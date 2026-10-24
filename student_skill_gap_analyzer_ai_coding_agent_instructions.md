# AI Coding-Agent Instruction Document
## Student Skill Gap Analyzer and Personalized Learning Roadmap Provider

**Document purpose:** This specification is the single source of truth for an AI coding agent implementing the Student Skill Gap Analyzer. Follow the requirements in order. Do not silently omit requirements or substitute fabricated job information.

---

## 1. Project overview

Build a portfolio-quality, full-stack web application that helps students understand the skill requirements of a target job at a company they choose, compare those requirements against their current skills, and receive a personalized learning roadmap.

The student must enter:
- Company name as free text.
- Target job role as free text (never require a predefined job-role dropdown).
- Current skills and self-reported proficiency.
- Weekly study hours.

The application must search for real, accessible, permitted job postings, prioritizing official company career pages and using additional public sources only where their access terms permit it. It must extract skills from the actual job description, preserve source evidence, compare verified requirements with student-reported skills, and produce a roadmap with free learning resources.

### Non-negotiable requirements
1. **No fabricated job requirements.** Never infer that a company requires a skill unless evidence from a verified job description supports it.
2. **No generic fallback job roles or skills.** If the company or matching role cannot be verified, return an explicit status and empty job/requirements lists.
3. **Traceability.** Every extracted requirement must link to a specific job snapshot and supporting text from the description.
4. **Current source data.** Search when the user requests an analysis. Do not use a hard-coded company-to-skill database as the source of truth.
5. **Historical snapshots are allowed.** Save analysis-specific snapshots for reproducibility, with fetched time, source URL, and freshness/staleness status. Do not present old snapshots as current without warning.
6. **Free/open-source first.** No paid APIs, paid AI services, paid hosting, paid authentication providers, or paid dashboards. The app must be useful without an LLM.
7. **Security and ownership.** Students may only read, update, or delete their own analyses and learning progress.
8. **Source compliance.** Respect robots.txt, website terms, rate limits, access controls, and applicable law. Do not bypass CAPTCHAs, logins, paywalls, blocks, or anti-bot protections.
9. **Honest UI.** Clearly distinguish required, preferred, inferred, and uncertain skills. Do not claim a skill is mandatory when the description does not establish that.
10. **No employment guarantees.** Skill coverage is an explanatory estimate, not a hiring probability or guarantee.

---

## 2. Target users and main user journey

### Student journey
1. Register or log in.
2. Open dashboard and start a new analysis.
3. Enter company name, target role, weekly study hours, and current skills/proficiency.
4. Submit an analysis.
5. Application searches permitted sources and verifies employer and role relevance.
6. Application displays verified postings with source links, posting details when available, fetch date, and any limitations.
7. Skills are extracted from each description with supporting evidence.
8. Application compares the required skills with the student's self-reported skills.
9. Application calculates a clearly explained coverage metric.
10. Application creates a learning roadmap within the weekly time budget.
11. Student marks roadmap items complete and views prior analyses.

### Empty/error journey
If no suitable job can be verified, show a plain-language status such as:
- `company_not_verified`
- `no_matching_jobs`
- `source_unavailable`
- `description_unavailable`
- `no_skills_extracted`

Return no invented job postings or requirements. Explain what happened and, where helpful, let the student retry or adjust the company/role text.

---

## 3. Required technology stack

Use free/open-source tools and avoid unnecessary dependencies.

### Frontend
- React with Vite (JavaScript; TypeScript is optional only if the project owner approves).
- Tailwind CSS v4, configured according to its current Vite integration.
- React Router for page navigation.
- Axios for API requests.
- Plotly.js for visualizations.

### Backend
- Python and FastAPI.
- Pydantic for request/response validation.
- SQLAlchemy ORM.
- SQLite for local development.
- Alembic migrations are recommended before schema changes become frequent.
- JWT access tokens using a maintained JWT library.
- Argon2 password hashing using a maintained password-hashing library.
- BeautifulSoup for permitted HTML parsing.
- pandas only where useful for structured processing.
- spaCy is optional; the initial extraction system should work without downloading a large language model.
- pytest and FastAPI TestClient/httpx for tests.

### Development and delivery
- Git and GitHub.
- Local development on Windows and VS Code.
- No paid hosting requirement. Provide local run instructions and an optional free-tier deployment guide only if current terms are verified; do not promise that a free tier will remain free.

### Avoid
- Paid LLM/API calls.
- Paid scraping APIs.
- Paid authentication or dashboard services.
- A mandatory external AI service.
- A static company-to-role/skill lookup table pretending to be live analysis.

---

## 4. Proposed repository structure

Create this structure incrementally. Do not create empty files for every feature on day one; implement one working vertical slice at a time.

```text
student-skill-gap-analyzer/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   │   ├── axios.js
│   │   │   ├── auth.js
│   │   │   ├── analyses.js
│   │   │   └── roadmap.js
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   ├── SkillCard.jsx
│   │   │   ├── SkillGapChart.jsx
│   │   │   ├── JobSourceCard.jsx
│   │   │   ├── LoadingState.jsx
│   │   │   └── ErrorState.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── pages/
│   │   │   ├── Register.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── NewAnalysis.jsx
│   │   │   ├── AnalysisResult.jsx
│   │   │   ├── Roadmap.jsx
│   │   │   └── NotFound.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── connectors/
│   │   │   ├── base.py
│   │   │   ├── official_careers.py
│   │   │   ├── greenhouse.py
│   │   │   └── lever.py
│   │   ├── security/
│   │   │   └── jwt_handler.py
│   │   └── resources/
│   │       └── learning_resources.json
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── .gitignore
└── README.md
```

Expected backend modules:
- `models/`: user, analysis, job snapshot, student skill, required skill, roadmap item, progress.
- `schemas/`: validated request and response schemas.
- `routes/`: auth, user, analyses, skills, roadmaps, progress.
- `services/`: company verification, job search, skill extraction, skill matching, roadmap generation.
- `connectors/`: source-specific integrations.
- `security/`: password hashing and JWT functions.
- `resources/`: curated free learning resource metadata, not company requirement data.
- `tests/`: unit, integration, source verification, security and ownership tests.

---

## 5. Database design

Use SQLAlchemy models with foreign keys, indexes, appropriate unique constraints, timestamps, and cascading behavior where appropriate. Use UTC timestamps in storage.

### 5.1 `users`
Fields:
- `id`: primary key.
- `name`: required string.
- `email`: required, normalized to lowercase, unique and indexed.
- `password_hash`: required; never store plaintext password.
- `created_at`, `updated_at`.

### 5.2 `analyses`
Fields:
- `id`: primary key.
- `user_id`: foreign key to users, indexed.
- `company_name`: user-entered text.
- `target_role`: user-entered text.
- `weekly_hours`: positive bounded number; reject zero/negative values.
- `status`: controlled status such as `pending`, `searching`, `verified_jobs_found`, `no_matching_jobs`, `source_unavailable`, `analysis_complete`, `failed`.
- `created_at`, `updated_at`.

### 5.3 `job_snapshots`
Fields:
- `id`: primary key.
- `analysis_id`: foreign key to analyses, indexed.
- `source_name`.
- `source_url`: validated HTTP(S) URL.
- `source_type`: e.g. official careers, public job feed, other permitted source.
- `employer_name`.
- `job_title`.
- `location`: optional.
- `employment_type`: optional.
- `description_text`: fetched description or a justified normalized excerpt; comply with source terms and retention constraints.
- `fetched_at`.
- `posted_at`: optional, only if the source provides it.
- `content_hash`: optional for deduplication/change detection.
- `is_stale`: boolean or derive from a configured freshness policy.
- `verification_status` and `verification_notes`.

Do not store more source content than permitted. Retain source URL and concise evidence when full description retention is not allowed.

### 5.4 `student_skills`
Fields:
- `id`: primary key.
- `analysis_id`: foreign key to analyses, indexed.
- `skill_name`: normalized display name.
- `canonical_skill`: normalized comparison key.
- `proficiency_level`: `beginner`, `intermediate`, `advanced`, or `unknown`.
- `self_reported`: boolean, normally true.
- `created_at`.

Allow multiple skills per analysis. Avoid accidental duplicates by normalizing aliases.

### 5.5 `required_skills`
Fields:
- `id`: primary key.
- `job_snapshot_id`: foreign key to job_snapshots, indexed.
- `skill_name`.
- `canonical_skill`.
- `requirement_type`: `required`, `preferred`, `mentioned`, or `uncertain`.
- `evidence_text`: supporting description text.
- `evidence_start` / `evidence_end`: optional offsets if reliable.
- `extraction_method`: e.g. `dictionary_phrase_match`, `nlp`, `manual_review`.
- `confidence`: optional, only if the extraction method defines a meaningful score.
- `created_at`.

Never add a required skill without a source snapshot and evidence.

### 5.6 `roadmap_items`
Use this name or `roadmaps` consistently; do not create two tables with overlapping purposes.
Fields:
- `id`: primary key.
- `analysis_id`: foreign key to analyses, indexed.
- `week_number`: positive integer.
- `skill_name` and `canonical_skill`.
- `learning_goal`.
- `resource_title`, `resource_url`, `resource_provider`.
- `estimated_hours`: non-negative numeric.
- `status`: `not_started`, `in_progress`, `completed`.
- `created_at`, `updated_at`.

### 5.7 `progress_records` (optional if roadmap item status is sufficient)
Fields:
- `id`: primary key.
- `roadmap_item_id`: foreign key to roadmap items.
- `completed_at`.
- `notes`.

For a simpler MVP, store current progress on roadmap items and add a separate event history only if needed.

### Relationships
- One user has many analyses.
- One analysis has many job snapshots.
- One job snapshot has many required skills.
- One analysis has many student skills.
- One analysis has many roadmap items.
- One roadmap item can have progress records if that table is implemented.

### Database rules
- Every analysis query must be scoped to the authenticated `user_id`.
- Do not trust a user-supplied `user_id` from request JSON.
- Index foreign keys and commonly searched columns.
- Use migrations once schema evolution begins.
- Use a development SQLite database; explain how to back up/delete local data.
- Never put database credentials or secrets in source control.

---

## 6. API contract

Use a consistent `/api` prefix and JSON responses. Add proper HTTP status codes, request validation, and predictable error shapes. API names may be refined, but keep frontend/backend contracts synchronized.

### Authentication
- `POST /api/auth/register`
  - Input: `name`, `email`, `password`.
  - Output: created user or access token according to the chosen consistent flow.
  - Reject invalid email, weak/too-long passwords, and duplicate email.
- `POST /api/auth/login`
  - Input: `email`, `password`.
  - Output: access token and safe user profile.
- `GET /api/auth/me`
  - Requires authentication.
  - Returns current user's safe profile only.

### Analyses
- `POST /api/analyses`
  - Authenticated.
  - Input: company, free-text target role, weekly study hours, and optionally student skills.
  - Creates an analysis and returns its ID/status.
- `GET /api/analyses`
  - Returns only the current user's analysis history.
- `GET /api/analyses/{analysis_id}`
  - Returns one owned analysis, its job snapshots, extracted skills and comparison results when ready.
- `DELETE /api/analyses/{analysis_id}`
  - Deletes only an analysis owned by the current user, according to a documented retention policy.
- `POST /api/analyses/{analysis_id}/search-jobs`
  - Runs permitted source connectors, verification and deduplication.
- `POST /api/analyses/{analysis_id}/run-gap-analysis`
  - Runs skill comparison on verified requirements and student skills.
- `POST /api/analyses/{analysis_id}/student-skills`
  - Creates/replaces the student's skill entries for that analysis, with validation.

### Roadmap and progress
- `GET /api/analyses/{analysis_id}/roadmap`
  - Returns the owned analysis's roadmap.
- `POST /api/analyses/{analysis_id}/roadmap`
  - Generates/re-generates a roadmap from verified gaps.
- `PATCH /api/roadmap-items/{item_id}`
  - Updates progress for an item only if its parent analysis belongs to the current user.

### Status/error conventions
Use explicit machine-readable status values, for example:
- `company_not_verified`
- `no_matching_jobs`
- `source_unavailable`
- `description_unavailable`
- `no_skills_extracted`
- `verified_jobs_found`
- `analysis_complete`

Never return HTTP 200 with fabricated or silently substituted requirements. Use an appropriate 4xx status for invalid input/unauthorized access, and a structured status in the response for a valid search that found no match. Avoid leaking stack traces or secrets to clients.

### Example request
```json
{
  "company_name": "TCS",
  "target_role": "Data Analyst",
  "weekly_hours": 8,
  "student_skills": [
    {"name": "Python", "proficiency": "intermediate"},
    {"name": "SQL", "proficiency": "beginner"},
    {"name": "Pandas", "proficiency": "intermediate"},
    {"name": "Power BI", "proficiency": "beginner"}
  ]
}
```

This is sample input only. It does not imply that any current TCS Data Analyst opening exists.

### Example verified-job response shape
```json
{
  "status": "verified_jobs_found",
  "company": "TCS",
  "target_role": "Data Analyst",
  "jobs": [
    {
      "title": "Actual title returned by a connector",
      "source_name": "Actual source name",
      "source_url": "https://actual-source.example/job",
      "fetched_at": "2026-10-24T12:00:00Z",
      "required_skills": [
        {
          "name": "SQL",
          "requirement_type": "required",
          "evidence_text": "Actual supporting text from the fetched description"
        }
      ]
    }
  ]
}
```

The domain and title above illustrate the schema only; never use placeholder data as a live result.

---

## 7. Job-source architecture and verification policy

This is the highest-risk functional area. Different employers use different career systems and terms. Build a connector architecture, not one universal scraper.

### 7.1 Common connector interface
Create an abstract base/interface with a method such as:
`search_jobs(company_name: str, target_role: str) -> list[NormalizedJob]`

A normalized job should contain:
- employer name;
- job title;
- source name and source URL;
- full or permitted description text;
- location, if available;
- posted date, if provided;
- fetched timestamp;
- source type;
- verification notes.

Each connector must handle timeouts, invalid responses, parsing changes, rate limits, and unavailable sources without crashing the entire analysis.

### 7.2 Source priority
1. Official company careers page or official company-provided feed/API.
2. Public ATS feeds/pages (for example Greenhouse or Lever) only when the employer uses that platform and the public endpoint is available under its terms.
3. Other public job sources only when their access terms and usage permit the intended use.

Do not assume all companies have a Greenhouse or Lever feed. Do not invent endpoint URLs. Implement source-specific connectors only after identifying and testing an actual supported source. Do not use paid job-search APIs.

### 7.3 Company verification
- Compare the employer identity in the returned job data with the user-entered company.
- Use a verified source-domain mapping only when it is established from a trustworthy official source; do not guess a domain from the company name.
- Do not count a job board's company-name text alone as definitive proof if the employer cannot be reasonably verified.
- Preserve the verification status and explanation.

### 7.4 Role relevance
- Match user-entered role to actual job titles/descriptions using normalized text and explainable relevance rules.
- Do not require the student to choose from a fixed role list.
- A broad or ambiguous role may return multiple clearly labeled matching postings.
- If relevance is weak, ask the user to refine the role or return no verified matching jobs.
- Do not silently replace the requested role with another role.

### 7.5 Source compliance and reliability
- Respect robots.txt, terms of service, applicable law, request limits, and access controls.
- Use reasonable timeouts and low request rates; cache only within permitted terms.
- Never bypass login, CAPTCHA, paywall, anti-bot measures, or technical blocks.
- Do not use search-engine snippets as a substitute for the actual description.
- Do not treat a job title alone as sufficient evidence for required skills.
- Record `fetched_at` and source URL for each snapshot.
- Define a freshness policy, e.g. show a warning when a snapshot is older than a configurable threshold. Do not assert that a listing is still open unless the source confirms it.
- Deduplicate with canonical URL and/or a content hash, while retaining provenance from multiple sources when useful.
- If a source is blocked or inaccessible, mark it unavailable and try other permitted connectors.
- If all connectors fail, return `source_unavailable`; if they work but find no suitable job, return `no_matching_jobs`.

---

## 8. Skill extraction and normalization

### MVP extraction
Implement a controlled skill vocabulary and alias mapping that is used only to recognize text in actual job descriptions, not to decide what a company requires.

Examples of alias normalization:
- `Postgres` -> `PostgreSQL`
- `Microsoft Power BI` -> `Power BI`
- case/spacing variants -> one canonical key

Do not merge unrelated skills merely because they are semantically similar. Keep the original displayed phrase and canonical key.

### Extraction steps
1. Normalize whitespace and text encoding without destroying source evidence.
2. Match multiword skill phrases before short phrases.
3. Use word boundaries/context where needed to avoid false matches (e.g. `R` should not match every letter r).
4. Preserve the exact supporting phrase/sentence from the description.
5. Determine requirement type (`required`, `preferred`, `mentioned`, `uncertain`) only when supported by context.
6. If context is ambiguous, label `uncertain` or `mentioned`; do not promote it to `required`.
7. Store extraction method and optional confidence only if meaningful.
8. Deduplicate canonical skills within each job snapshot while retaining useful evidence occurrences.

spaCy or other local NLP tools can be added later. No paid AI model is required. If a model is added, its output must still be grounded in source text and must not invent requirements.

---

## 9. Skill-gap matching and scoring

### Student proficiency
Use:
- `unknown` / not supplied;
- `beginner`;
- `intermediate`;
- `advanced`.

These are student self-reports, not independently verified ability.

### Status rules
For each verified requirement:
- No matching student skill: `needs_assessment` or `missing` (make the distinction clear: not reported does not prove the student cannot do it).
- Student says beginner: `needs_improvement` only when the description provides evidence that a higher level is expected; otherwise `proficiency_unspecified`.
- Student says intermediate/advanced: `self_reported_covered`, not “guaranteed qualified.”
- Skill appears in student's profile but not in verified job requirements: `additional_skill`.
- Requirement extraction is ambiguous: `uncertain_requirement`.

Never assume a job posting requires advanced proficiency if it does not say so.

### Coverage score
A simple first version may calculate:
`coverage = count_of_required_skills_marked_self_reported_covered / count_of_verified_required_skills * 100`

Rules:
- Only use skills with the `required` classification in the denominator.
- If no verified required skills exist, return `null`/“Not enough verified data,” not 0%.
- Explain that coverage is a rough, self-reported skills comparison, not an employability score.
- Avoid double-counting the same canonical skill across multiple jobs. Either show per-job results or define a transparent aggregation method.
- Display job count and source/freshness information alongside the metric.

---

## 10. Learning roadmap generation

Generate a rules-based roadmap using verified gaps and a curated list of genuinely free learning resources.

### Inputs
- verified required skills and requirement type;
- student-reported skills/proficiency;
- weekly study hours;
- resource catalog with title, URL, provider, topic, access status and last-checked date.

### Rules
1. Prioritize missing/unassessed and weak skills that are explicitly required by the verified posting.
2. Keep optional/preferred skills lower priority than required skills unless the student chooses otherwise.
3. Do not invent a required skill to fill a weekly schedule.
4. Estimate effort transparently; treat estimates as guidance, not facts about the student's ability.
5. Sum planned hours for each week and do not exceed the student's weekly availability.
6. If the available hours are too low for all goals, extend the plan over more weeks rather than overloading a week.
7. Provide specific learning goals and practical exercises.
8. Use free resources only and verify links/access status. Do not label a paid course as free.
9. If no appropriate free resource is known, say so and suggest a general learning objective without fabricating a link.
10. Save the generated roadmap and let students update progress.
11. When the job evidence changes, offer to regenerate the roadmap and retain a timestamped analysis history.

The roadmap must be useful without an LLM. An optional local model may be considered later, but it must not be required for the MVP.

---

## 11. Frontend requirements

### Pages
1. **Register:** name, email, password, validation and clear errors.
2. **Login:** email/password and clear authentication errors.
3. **Dashboard:** create new analysis and list prior analyses/statuses.
4. **New Analysis:** company text input, role text input, weekly hours, add/remove skill entries and proficiency selectors.
5. **Analysis Result:** source cards, verified postings, evidence-backed skills, student-vs-required comparison, coverage explanation, freshness and error states.
6. **Roadmap:** week-by-week tasks, time estimates, free resource links and progress controls.
7. **Not Found:** friendly 404 page.

### UX requirements
- No job-role dropdown.
- Show progress/loading states during searches.
- Make source links clickable and visibly distinguish official vs third-party sources.
- Clearly label user-reported skills and extracted requirements.
- Provide accessible labels, keyboard navigation, readable contrast, and responsive layouts.
- Do not show a fake chart or fake successful result when no verified data exists.
- Handle network failures and expired sessions.
- Confirm destructive actions such as deleting an analysis.
- Explain the meaning and limits of the coverage metric.

### Authentication storage
For production, prefer secure, HttpOnly, Secure, SameSite cookies with suitable CSRF protection where applicable. If using bearer tokens in browser storage for a local MVP, document the XSS risk, avoid storing secrets, and do not call that production-hardened. Do not place tokens in URLs or logs.

---

## 12. Configuration and secrets

Provide `.env.example` files, never real secrets.

Backend example:
```dotenv
APP_NAME=Student Skill Gap Analyzer
DATABASE_URL=sqlite:///./app.db
JWT_SECRET=replace_with_a_long_random_secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_ORIGIN=http://localhost:5173
```

Requirements:
- Load settings through a configuration module.
- Fail safely if the production JWT secret is missing or still a known placeholder.
- Keep `.env`, local databases, virtual environments, caches, `node_modules`, and build outputs out of Git.
- Provide a `.gitignore`.
- Never log passwords, full tokens, or secrets.
- Keep frontend environment variables public; never put backend secrets in Vite variables.

---

## 13. Security and privacy

- Hash passwords with Argon2 or another maintained secure password-hashing scheme.
- Normalize and uniquely constrain email.
- Validate and bound all inputs (company, role, skill names, weekly hours, pagination).
- Use parameterized ORM queries.
- Authenticate private routes and enforce analysis ownership at the database-query level.
- Avoid insecure direct object reference (IDOR) vulnerabilities.
- Restrict CORS to configured frontend origins.
- Set timeouts and response-size limits for external fetches.
- Prevent SSRF: do not let a user submit an arbitrary URL for the backend to fetch without allowlisting/validation. Resolve only configured/verified source URLs, block private/internal IP ranges and unsafe schemes, and revalidate redirects.
- Handle redirects safely and prevent access to cloud metadata/internal services.
- Sanitize displayed HTML/text; never render raw external job HTML unsafely.
- Avoid collecting unnecessary personal data.
- Define analysis deletion and source snapshot retention behavior.
- Do not store entire descriptions where source terms do not permit it.
- Add rate limits for registration, login, and expensive searches where feasible without paid services.
- Return safe error messages; log technical details server-side without sensitive data.

---

## 14. Testing strategy

Write tests as features are implemented, not only at the end.

### Authentication tests
- Successful registration/login.
- Duplicate email rejected.
- Wrong password rejected.
- Expired/invalid token rejected.
- Password is hashed and never returned.
- Private endpoint rejects unauthenticated request.

### Ownership tests
- User A cannot read, modify or delete User B's analysis.
- User A cannot update User B's roadmap item.
- Request body cannot override the authenticated user ID.

### Connector and verification tests
Use mocked HTTP responses and saved fixtures; automated tests should not depend on live third-party websites.
- Valid source record normalized.
- Invalid HTML, timeout and HTTP errors handled.
- Employer mismatch rejected.
- Role mismatch does not silently become a match.
- Missing description returns `description_unavailable`.
- All sources unavailable returns `source_unavailable`.
- Working sources with no match return `no_matching_jobs`.
- Duplicate postings deduplicated.
- Source URL and fetched timestamp preserved.
- Connector follows configured terms and limits; no bypass logic exists.

### Skill extraction tests
- Exact skill phrase extracted from fixture.
- Evidence text is preserved.
- Multiword skill matched correctly.
- False positives avoided (especially short names such as `R`).
- Alias normalization works.
- Ambiguous text does not become a confirmed required skill.
- No evidence means no required-skill record.
- Same skill is not double-counted.

### Matching and scoring tests
- Missing/not-reported is not described as proven inability.
- Proficiency is not invented from a job description.
- Only verified `required` skills enter the coverage denominator.
- Zero verified required skills yields `null`/not enough data.
- Duplicate requirements do not inflate coverage.

### Roadmap tests
- Only verified gaps drive required-skill goals.
- Weekly allocated hours never exceed the student's limit.
- A plan expands across weeks when necessary.
- Resource links are from the curated catalog and marked free only when verified.
- No unsupported link is fabricated.
- Progress updates persist and enforce ownership.

### Frontend checks
- Forms validate.
- Role is a free-text input.
- Loading, empty, success and error states display correctly.
- Source links open correctly.
- Expired sessions are handled.
- Layout works on mobile and desktop.
- No false successful result is displayed.

Run backend tests with `pytest`. Add linting/formatting if useful, but do not let tooling complexity delay the first working vertical slice.

---

## 15. Implementation phases and required deliverables

### Phase 1 — Foundation
Tasks:
- Create repository and virtual environment.
- Create FastAPI app and health endpoint.
- Configure SQLite and SQLAlchemy.
- Add config, `.env.example`, `.gitignore`, and README.
Deliverable: app starts locally and database connection is tested.

### Phase 2 — Authentication
Tasks:
- User model and schemas.
- Registration/login.
- Argon2 hashing and JWT verification.
- `/api/auth/me`.
- Tests for auth and private endpoints.
Deliverable: secure local auth flow.

### Phase 3 — Analysis input and persistence
Tasks:
- Analysis and student-skill models.
- Create/list/get/delete analysis endpoints.
- Free-text company and role validation.
- Ownership checks.
Deliverable: student can save and revisit an analysis.

### Phase 4 — First verified source connector
Tasks:
- Define connector interface and normalized job schema.
- Choose one real, accessible source after checking its documentation/terms.
- Implement parsing, timeouts, source verification and tests.
- Do not invent endpoints or claim live support for untested companies.
Deliverable: one real source can return a verifiable job or a clear failure status.

### Phase 5 — Multiple source connectors
Tasks:
- Add other official/public feeds only where actually supported and permitted.
- Merge and deduplicate results.
- Record source provenance and freshness.
Deliverable: source aggregation with graceful failure.

### Phase 6 — Skill extraction and gap analysis
Tasks:
- Canonical skills and alias mapping.
- Evidence-backed extraction.
- Per-job comparison and coverage score.
- Tests for false positives and empty data.
Deliverable: explainable skill-gap results.

### Phase 7 — Roadmap and progress
Tasks:
- Curated free resource catalog.
- Prioritization and weekly scheduling.
- Persist roadmap items and completion status.
Deliverable: personalized plan within weekly hours.

### Phase 8 — Frontend integration
Tasks:
- Auth pages and protected routes.
- Dashboard and analysis form.
- Result and roadmap views.
- Charts, loading/error/empty states.
Deliverable: full end-to-end browser workflow.

### Phase 9 — Hardening and portfolio release
Tasks:
- Run full test suite.
- Fix authorization, source and edge-case failures.
- Add responsive styling and accessibility checks.
- Write setup, architecture, limitations, screenshots and API instructions in README.
- Verify all setup commands from a clean environment.
Deliverable: portfolio-ready local application.

---

## 16. Local development commands (Windows PowerShell)

### Backend setup
```powershell
mkdir student-skill-gap-analyzer
cd student-skill-gap-analyzer
mkdir backend
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1

python -m pip install fastapi "uvicorn[standard]" sqlalchemy
python -m pip install pydantic-settings email-validator
python -m pip install pyjwt "pwdlib[argon2]"
python -m pip install python-multipart beautifulsoup4 pandas
python -m pip install pytest httpx

pip freeze > requirements.txt
uvicorn app.main:app --reload
```

The agent must provide a complete `app/main.py` and required package files before asking the user to run Uvicorn. If PowerShell blocks virtual environment activation, explain a scoped, safe fix instead of changing machine-wide policy blindly.

### Frontend setup
From the repository root in a separate terminal:
```powershell
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install axios react-router-dom
npm run dev
```

Configure Tailwind CSS v4 using its current Vite integration and ensure the frontend API base URL is configurable. Run backend and frontend in separate terminals. Configure CORS for the actual local frontend origin.

### Testing
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest
```

The README must include working commands, environment setup, database behavior, test commands, API docs URL, and troubleshooting tips.

---

## 17. Acceptance criteria (definition of done)

The project is not complete until all of the following are demonstrated:

1. A student can register, log in, and log out.
2. Passwords are hashed and protected endpoints require authentication.
3. A student can type any company name and target role as free text.
4. The application attempts live retrieval from implemented, permitted sources.
5. The application displays actual job titles and source links, with fetch timestamps.
6. Employer and role relevance are checked before a posting is used.
7. Required skills are supported by actual description evidence.
8. The UI distinguishes required, preferred, mentioned, uncertain, and student-reported skills.
9. Skill-gap results do not invent proficiency requirements.
10. The coverage metric has a clear formula and handles no-data cases correctly.
11. If no verified matching posting is found, the UI displays a clear no-match/source-unavailable status with no generic fabricated results.
12. The roadmap uses verified gaps, curated free resources, and does not exceed weekly study hours.
13. Students can save progress and revisit prior analyses.
14. A student cannot access another student's analyses or roadmap items.
15. External-source errors and timeouts do not crash the app.
16. Automated tests cover auth, ownership, connectors, extraction, matching and roadmap scheduling.
17. The application runs locally using the documented instructions without paid services.
18. README explains architecture, limitations, sources, setup, tests, and how to add a new permitted connector.

---

## 18. Instructions to the AI coding agent

Work incrementally and keep the application runnable after every phase.

For each phase:
1. Inspect the current repository before editing.
2. Summarize the specific files to create/change.
3. Implement a small, complete vertical slice.
4. Provide full code for each new/changed file, not vague pseudocode.
5. Explain the purpose of important code in beginner-friendly language.
6. Give exact Windows PowerShell commands to run.
7. Add or update tests.
8. Run tests and report actual outcomes; never claim tests passed without running them.
9. Fix failures before moving on.
10. Keep frontend and backend schemas synchronized.
11. Do not replace existing working code wholesale unless necessary; explain migrations and changes.
12. Never hard-code fake successful jobs, fake company requirements, fake links, or fake source responses in production paths. Mock data is allowed only in clearly labeled tests/demo mode.
13. If a live source is not verifiable or accessible, state that limitation and implement an honest fallback status.
14. Do not add paid services or require an LLM.
15. Ask a question only if a missing decision genuinely blocks progress; otherwise choose a safe, documented default.

### First task for the agent
Start with **Phase 1 only**:
- Inspect/create the repository.
- Create a minimal FastAPI application, configuration, SQLite connection, and health endpoint.
- Add `.env.example`, `.gitignore`, and a concise README.
- Add a basic test for the health endpoint and database connection.
- Give exact Windows PowerShell commands and verify the app runs before proceeding to authentication.

Do not attempt to generate the entire codebase in one untested response. Build and validate it in phases.
