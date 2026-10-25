from datetime import datetime, timezone
import pytest

from app.models.analysis import Analysis
from app.models.student_skill import StudentSkill
from app.models.job_snapshot import JobSnapshot
from app.models.required_skill import RequiredSkill
from app.services.skill_extractor import extract_skills_from_text
from app.services.gap_analyzer import compute_skill_gap_analysis


def test_extract_skills_multiword_and_evidence():
    """Verifies that multi-word skills and exact supporting sentences are cleanly extracted."""
    text = (
        "About Us:\nWe build modern software.\n\n"
        "Requirements:\n"
        "• Minimum 3 years experience with Python and PostgreSQL.\n"
        "• Strong proficiency in Google Cloud Platform and Docker containers.\n\n"
        "Preferred Qualifications:\n"
        "• Experience with React and TypeScript is a plus.\n"
    )

    extracted = extract_skills_from_text(text)
    canonical_map = {item.canonical_skill: item for item in extracted}

    # Verify extracted skills exist
    assert "python" in canonical_map
    assert "postgresql" in canonical_map
    assert "gcp" in canonical_map or "google cloud platform" in canonical_map
    assert "docker" in canonical_map
    assert "react" in canonical_map
    assert "typescript" in canonical_map

    # Check evidence preservation
    python_skill = canonical_map["python"]
    assert "experience with Python and PostgreSQL" in python_skill.evidence_text
    assert python_skill.requirement_type == "required"

    react_skill = canonical_map["react"]
    assert "is a plus" in react_skill.evidence_text
    assert react_skill.requirement_type == "preferred"


def test_avoid_short_symbol_false_positives():
    """Verifies that common words like 'go', 'a', 'to' do not create false matches for Go or R."""
    negative_text = "We expect team members to go above and beyond to create a great company culture."
    extracted = extract_skills_from_text(negative_text)
    extracted_canonical = [item.canonical_skill for item in extracted]
    assert "go" not in extracted_canonical
    assert "r" not in extracted_canonical

    positive_text = "Must have strong experience with Go programming, C++, and Python."
    pos_extracted = extract_skills_from_text(positive_text)
    pos_canonical = {item.canonical_skill: item for item in pos_extracted}
    assert "go" in pos_canonical
    assert "c++" in pos_canonical
    assert "python" in pos_canonical


def test_coverage_calculation_formula(db_session):
    """
    Verifies that coverage is strictly computed as:
    (covered_required / total_required) * 100
    with correct classification of beginner and missing skills.
    """
    now = datetime.now(timezone.utc)
    analysis = Analysis(
        user_id=1,
        company_name="Stripe",
        target_role="Backend Engineer",
        weekly_hours=10,
        status="verified_jobs_found",
    )
    db_session.add(analysis)
    db_session.flush()

    # Student skills:
    # Python: intermediate (covered)
    # SQL: advanced (covered)
    # Docker: beginner (needs_improvement)
    # (Kubernetes is missing)
    # React: intermediate (additional_skill not required by employer)
    skills = [
        StudentSkill(analysis_id=analysis.id, skill_name="Python", canonical_skill="python", proficiency_level="intermediate"),
        StudentSkill(analysis_id=analysis.id, skill_name="SQL", canonical_skill="sql", proficiency_level="advanced"),
        StudentSkill(analysis_id=analysis.id, skill_name="Docker", canonical_skill="docker", proficiency_level="beginner"),
        StudentSkill(analysis_id=analysis.id, skill_name="React", canonical_skill="react", proficiency_level="intermediate"),
    ]
    db_session.add_all(skills)

    # Job snapshot with 4 required skills: Python, SQL, Docker, Kubernetes
    # and 1 preferred skill: GraphQL
    snapshot = JobSnapshot(
        analysis_id=analysis.id,
        source_name="Greenhouse",
        source_url="https://boards.greenhouse.io/stripe/jobs/1",
        source_type="public_ats_feed",
        employer_name="Stripe",
        job_title="Backend Engineer",
        description_text="Job description",
        fetched_at=now,
        verification_status="verified",
    )
    db_session.add(snapshot)
    db_session.flush()

    reqs = [
        RequiredSkill(job_snapshot_id=snapshot.id, skill_name="Python", canonical_skill="python", requirement_type="required", evidence_text="Python required."),
        RequiredSkill(job_snapshot_id=snapshot.id, skill_name="SQL", canonical_skill="sql", requirement_type="required", evidence_text="SQL required."),
        RequiredSkill(job_snapshot_id=snapshot.id, skill_name="Docker", canonical_skill="docker", requirement_type="required", evidence_text="Docker required."),
        RequiredSkill(job_snapshot_id=snapshot.id, skill_name="Kubernetes", canonical_skill="kubernetes", requirement_type="required", evidence_text="Kubernetes required."),
        RequiredSkill(job_snapshot_id=snapshot.id, skill_name="GraphQL", canonical_skill="graphql", requirement_type="preferred", evidence_text="GraphQL is a plus."),
    ]
    db_session.add_all(reqs)
    db_session.commit()
    db_session.refresh(analysis)

    result = compute_skill_gap_analysis(analysis)

    # Total strictly required skills in denominator = 4 (Python, SQL, Docker, Kubernetes)
    # GraphQL is preferred, so it must not be in the denominator!
    assert result.unique_required_count == 4
    # Covered = 2 (Python, SQL)
    assert result.covered_required_count == 2
    # Needs improvement = 1 (Docker - beginner)
    assert result.needs_improvement_count == 1
    # Missing = 1 (Kubernetes - not reported)
    assert result.missing_required_count == 1

    # Expected coverage = (2 / 4) * 100 = 50.0%
    assert result.coverage_percentage == 50.0

    # Verify React is recognized as an additional skill
    additional_canonicals = [a["canonical_skill"] for a in result.additional_skills]
    assert "react" in additional_canonicals


def test_zero_required_skills_yields_null_coverage(db_session):
    """Verifies that if zero strictly required skills are found, coverage is None (not 0%)."""
    now = datetime.now(timezone.utc)
    analysis = Analysis(user_id=1, company_name="Corp", target_role="Role", weekly_hours=5, status="pending")
    db_session.add(analysis)
    db_session.flush()

    snapshot = JobSnapshot(
        analysis_id=analysis.id,
        source_name="Lever",
        source_url="https://jobs.lever.co/corp/1",
        source_type="public_ats_feed",
        employer_name="Corp",
        job_title="Role",
        description_text="Text",
        fetched_at=now,
        verification_status="verified",
    )
    db_session.add(snapshot)
    db_session.flush()

    # Only a preferred skill
    req = RequiredSkill(
        job_snapshot_id=snapshot.id,
        skill_name="Python",
        canonical_skill="python",
        requirement_type="preferred",
        evidence_text="Python is nice to have.",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(analysis)

    result = compute_skill_gap_analysis(analysis)
    assert result.coverage_percentage is None
    assert "Not enough verified required skills" in result.coverage_explanation


def test_api_run_gap_analysis_integration(client, db_session):
    """
    Integration test verifying POST /api/analyses/{id}/run-gap-analysis
    extracts requirements, saves RequiredSkill models, and returns full gap payload.
    """
    # 1. Register student
    reg = client.post(
        "/api/auth/register",
        json={"name": "Alex GapTester", "email": "alex.gap@example.com", "password": "Password123!"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    # 2. Create analysis with student skills
    create_res = client.post(
        "/api/analyses",
        json={
            "company_name": "Cloudflare",
            "target_role": "Systems Engineer",
            "weekly_hours": 12,
            "student_skills": [
                {"name": "Python", "proficiency": "intermediate"},
                {"name": "Linux", "proficiency": "beginner"},
            ],
        },
        headers=headers,
    )
    analysis_id = create_res.json()["id"]

    # 3. Insert mock snapshot into DB
    now = datetime.now(timezone.utc)
    snapshot = JobSnapshot(
        analysis_id=analysis_id,
        source_name="Greenhouse",
        source_url="https://boards.greenhouse.io/cloudflare/101",
        source_type="public_ats_feed",
        employer_name="Cloudflare",
        job_title="Systems Engineer",
        description_text=(
            "Responsibilities:\nBuild global network infrastructure.\n\n"
            "Requirements:\n"
            "• Strong proficiency in Python and Linux.\n"
            "• Experience with Docker and Kubernetes is required.\n"
        ),
        fetched_at=now,
        verification_status="verified",
    )
    db_session.add(snapshot)
    db_session.commit()

    # 4. Call run-gap-analysis endpoint
    gap_res = client.post(f"/api/analyses/{analysis_id}/run-gap-analysis", headers=headers)
    assert gap_res.status_code == 200
    data = gap_res.json()

    assert data["analysis_id"] == analysis_id
    assert data["company_name"] == "Cloudflare"
    assert data["target_role"] == "Systems Engineer"
    assert data["coverage_percentage"] is not None
    assert len(data["skill_gaps"]) >= 4

    # Verify RequiredSkill records were saved in database
    db_reqs = db_session.query(RequiredSkill).filter(RequiredSkill.job_snapshot_id == snapshot.id).all()
    assert len(db_reqs) >= 4
    for r in db_reqs:
        assert r.evidence_text is not None
        assert len(r.evidence_text) > 0


def test_run_gap_analysis_without_snapshots_fails_400(client):
    """Verifies that running gap analysis without first fetching job snapshots returns 400."""
    reg = client.post(
        "/api/auth/register",
        json={"name": "No Snapshot User", "email": "nosnapshot@example.com", "password": "Password123!"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    create_res = client.post(
        "/api/analyses",
        json={"company_name": "TestCorp", "target_role": "Analyst", "weekly_hours": 8},
        headers=headers,
    )
    analysis_id = create_res.json()["id"]

    res = client.post(f"/api/analyses/{analysis_id}/run-gap-analysis", headers=headers)
    assert res.status_code == 400
    assert "No verified job postings found" in res.json()["detail"]


def test_run_gap_analysis_ownership_isolation(client):
    """Verifies that User B cannot trigger gap analysis on User A's analysis."""
    reg_a = client.post(
        "/api/auth/register",
        json={"name": "User A", "email": "owner.a@example.com", "password": "Password123!"},
    )
    headers_a = {"Authorization": f"Bearer {reg_a.json()['access_token']}"}

    reg_b = client.post(
        "/api/auth/register",
        json={"name": "User B", "email": "intruder.b@example.com", "password": "Password123!"},
    )
    headers_b = {"Authorization": f"Bearer {reg_b.json()['access_token']}"}

    create_res = client.post(
        "/api/analyses",
        json={"company_name": "SecureCorp", "target_role": "Engineer", "weekly_hours": 10},
        headers=headers_a,
    )
    analysis_id = create_res.json()["id"]

    res = client.post(f"/api/analyses/{analysis_id}/run-gap-analysis", headers=headers_b)
    assert res.status_code == 404
