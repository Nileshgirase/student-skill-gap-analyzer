import pytest
from datetime import datetime, timezone
from app.services.job_search_service import (
    find_cached_snapshots,
    apply_cached_snapshot_to_analysis,
)
from app.models.analysis import Analysis
from app.models.job_snapshot import JobSnapshot
from app.models.user import User


def test_find_cached_snapshots_from_catalog(db_session):
    """Verifies that find_cached_snapshots locates verified historical postings from catalog."""
    matches = find_cached_snapshots(
        company_name="Google",
        target_role="Software Engineer",
        db=db_session,
    )
    assert len(matches) >= 1
    first = matches[0]
    assert first["employer_name"] == "Google"
    assert "Software Engineer" in first["job_title"]
    assert first["source"] == "archived_catalog"
    assert "Python" in first["description_text"]


def test_find_cached_snapshots_from_database_precedence(db_session):
    """Verifies that existing database snapshots are found and prioritized."""
    user = User(name="Test Student", email="test.cache@university.edu", password_hash="dummy")
    db_session.add(user)
    db_session.commit()

    analysis1 = Analysis(user_id=user.id, company_name="GitLab", target_role="Backend Engineer", weekly_hours=10)
    db_session.add(analysis1)
    db_session.commit()

    # Add a verified snapshot to the DB
    snap = JobSnapshot(
        analysis_id=analysis1.id,
        source_name="Greenhouse",
        source_url="https://boards.greenhouse.io/gitlab/jobs/1",
        source_type="public_ats_feed",
        employer_name="GitLab",
        job_title="Senior Backend Engineer",
        description_text="Must have strong experience with Ruby, Go, and PostgreSQL.",
        fetched_at=datetime.now(timezone.utc),
        is_stale=False,
        verification_status="verified",
    )
    db_session.add(snap)
    db_session.commit()

    # Now create analysis2 for GitLab and search cached
    analysis2 = Analysis(user_id=user.id, company_name="GitLab", target_role="Backend Engineer", weekly_hours=10)
    db_session.add(analysis2)
    db_session.commit()

    matches = find_cached_snapshots(
        company_name="GitLab",
        target_role="Backend Engineer",
        db=db_session,
        exclude_analysis_id=analysis2.id,
    )
    assert len(matches) >= 1
    assert matches[0]["source"] == "database_cache"
    assert matches[0]["job_title"] == "Senior Backend Engineer"


def test_apply_cached_snapshot_to_analysis(db_session):
    """Verifies that apply_cached_snapshot_to_analysis links an archived snapshot with stale flags."""
    user = User(name="Test User", email="apply.cache@university.edu", password_hash="dummy")
    db_session.add(user)
    db_session.commit()

    analysis = Analysis(user_id=user.id, company_name="Microsoft", target_role="Software Engineer", weekly_hours=8)
    db_session.add(analysis)
    db_session.commit()

    snapshots = apply_cached_snapshot_to_analysis(analysis=analysis, db=db_session)
    assert len(snapshots) == 1
    snap = snapshots[0]
    assert snap.employer_name == "Microsoft"
    assert snap.is_stale is True
    assert snap.verification_status == "archived_snapshot"
    assert "Archived snapshot loaded" in snap.verification_notes
    assert analysis.status == "archived_jobs_found"


def test_api_use_cached_posting_and_run_gap_analysis(client):
    """End-to-end test for using cached posting when live search has no verified board."""
    # 1. Register student
    reg = client.post(
        "/api/auth/register",
        json={"name": "Archive Tester", "email": "archive.tester@university.edu", "password": "SecurePassword123!"},
    )
    assert reg.status_code == 201
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    # 2. Create analysis for Google Software Engineer
    create_res = client.post(
        "/api/analyses",
        headers=headers,
        json={
            "company_name": "Google",
            "target_role": "Software Engineer",
            "weekly_hours": 10,
            "student_skills": [
                {"name": "Python", "proficiency": "intermediate"},
                {"name": "Git", "proficiency": "beginner"},
            ],
        },
    )
    assert create_res.status_code == 201
    analysis_id = create_res.json()["id"]

    # 3. Live search for Google should return company_not_verified but indicate cached postings exist
    search_res = client.post(f"/api/analyses/{analysis_id}/search-jobs", headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["status"] == "company_not_verified"
    assert search_data["has_cached_snapshots"] is True
    assert search_data["cached_snapshot_count"] >= 1
    assert "Software Engineer" in search_data["cached_snapshot_title"]

    # 4. Invoke use-cached-posting endpoint
    use_cached_res = client.post(f"/api/analyses/{analysis_id}/use-cached-posting", headers=headers)
    assert use_cached_res.status_code == 200
    used_data = use_cached_res.json()
    assert used_data["status"] == "archived_jobs_found"
    assert len(used_data["jobs"]) == 1
    assert used_data["jobs"][0]["is_stale"] is True
    assert used_data["jobs"][0]["verification_status"] == "archived_snapshot"

    # 5. Run gap analysis on the archived snapshot
    gap_res = client.post(f"/api/analyses/{analysis_id}/run-gap-analysis", headers=headers)
    assert gap_res.status_code == 200
    gap_data = gap_res.json()
    assert gap_data["coverage_percentage"] is not None
    assert len(gap_data["skill_gaps"]) >= 3
    # Check that Python is covered and others are missing/needs_improvement with evidence
    assert any(g["canonical_skill"] == "python" and g["status"] == "self_reported_covered" for g in gap_data["skill_gaps"])
    assert any("evidence_text" in g and g["evidence_text"] is not None for g in gap_data["skill_gaps"])

    # 6. Generate roadmap from the archived gap analysis
    roadmap_res = client.post(f"/api/analyses/{analysis_id}/roadmap", headers=headers)
    assert roadmap_res.status_code == 201
    roadmap_data = roadmap_res.json()
    assert len(roadmap_data["items"]) >= 1


def test_find_cached_snapshots_for_hcltech_and_alias(db_session):
    """Verifies that HCLTech and aliases like HCL match the archived catalog."""
    matches1 = find_cached_snapshots(
        company_name="HCLTech",
        target_role="Software Engineer",
        db=db_session,
    )
    assert len(matches1) >= 1
    assert matches1[0]["employer_name"] == "HCLTech"
    assert "Java" in matches1[0]["description_text"]

    matches2 = find_cached_snapshots(
        company_name="HCL",
        target_role="Software Engineer",
        db=db_session,
    )
    assert len(matches2) >= 1
    assert matches2[0]["employer_name"] == "HCLTech"


def test_api_paste_job_description_flow(client):
    """Verifies that a student can directly paste a job description for any company."""
    # 1. Register student
    reg = client.post(
        "/api/auth/register",
        json={"name": "HCL Student", "email": "hcl.student@university.edu", "password": "SecurePassword123!"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    # 2. Create analysis for HCLTech Java Developer
    create_res = client.post(
        "/api/analyses",
        headers=headers,
        json={
            "company_name": "HCLTech",
            "target_role": "Java Developer",
            "weekly_hours": 12,
            "student_skills": [
                {"name": "Java", "proficiency": "intermediate"},
                {"name": "Git", "proficiency": "beginner"},
            ],
        },
    )
    assert create_res.status_code == 201
    analysis_id = create_res.json()["id"]

    # 3. Paste job description directly
    paste_res = client.post(
        f"/api/analyses/{analysis_id}/paste-job-description",
        headers=headers,
        json={
            "description_text": (
                "HCLTech is seeking an experienced Java Developer. "
                "Required: Strong proficiency in Java, Spring Boot, and REST API development. "
                "Required: Hands-on experience with PostgreSQL and SQL database queries. "
                "Experience with Docker and AWS is a plus."
            ),
            "job_title": "Java Developer",
            "source_url": "https://www.hcltech.com/careers/java-dev",
        },
    )
    assert paste_res.status_code == 200
    paste_data = paste_res.json()
    assert paste_data["status"] == "verified_jobs_found"
    assert len(paste_data["jobs"]) == 1
    assert paste_data["jobs"][0]["source_type"] == "user_provided_posting"

    # 4. Run gap analysis on the pasted posting
    gap_res = client.post(f"/api/analyses/{analysis_id}/run-gap-analysis", headers=headers)
    assert gap_res.status_code == 200
    gap_data = gap_res.json()

    # Java should be covered (intermediate), Spring Boot & PostgreSQL missing (required)
    assert gap_data["coverage_percentage"] is not None
    assert any(g["canonical_skill"] == "java" and g["status"] == "self_reported_covered" for g in gap_data["skill_gaps"])
    assert any(g["canonical_skill"] == "spring boot" and g["status"] == "missing" for g in gap_data["skill_gaps"])

    # 5. Generate roadmap
    roadmap_res = client.post(f"/api/analyses/{analysis_id}/roadmap", headers=headers)
    assert roadmap_res.status_code == 201
    assert len(roadmap_res.json()["items"]) >= 1
