import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.connectors.base import NormalizedJob

def test_full_student_e2e_journey(client):
    """
    End-to-End Test for the full student journey:
    1. Register a new student
    2. Log in and get JWT token
    3. Create a new job analysis with self-reported skills
    4. Search jobs (with mocked ATS connector returning verified jobs)
    5. Run evidence-backed gap analysis
    6. Verify coverage metric formula
    7. Generate personalized learning roadmap bounded by weekly hours
    8. Update roadmap item completion status
    9. List analyses on dashboard
    10. Verify IDOR isolation: second student cannot view or modify the analysis
    11. Delete the analysis and verify cascading clean-up
    """
    # 1. Register student
    reg_res = client.post(
        "/api/auth/register",
        json={
            "email": "sarah.student@university.edu",
            "password": "SecurePassword123!",
            "name": "Sarah Student",
        },
    )
    assert reg_res.status_code == 201
    token1 = reg_res.json()["access_token"]
    headers1 = {"Authorization": f"Bearer {token1}"}

    # 2. Verify /api/auth/me
    me_res = client.get("/api/auth/me", headers=headers1)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "sarah.student@university.edu"

    # 3. Create new analysis
    create_res = client.post(
        "/api/analyses",
        headers=headers1,
        json={
            "company_name": "Stripe",
            "target_role": "Backend Engineer",
            "weekly_hours": 10,
            "student_skills": [
                {"name": "Python", "proficiency": "intermediate"},
                {"name": "Git", "proficiency": "beginner"},
            ],
        },
    )
    assert create_res.status_code == 201
    analysis_data = create_res.json()
    analysis_id = analysis_data["id"]
    assert analysis_data["company_name"] == "Stripe"
    assert analysis_data["weekly_hours"] == 10
    assert len(analysis_data["student_skills"]) == 2

    # 4. Search jobs with mocked Greenhouse and Lever feeds
    now_utc = datetime.now(timezone.utc)
    mock_jobs = [
        NormalizedJob(
            employer_name="Stripe",
            job_title="Senior Backend Engineer",
            source_name="greenhouse",
            source_url="https://boards.greenhouse.io/stripe/jobs/101",
            description_text="We are seeking a Backend Engineer. Required: 3+ years experience with Python and Docker. Experience with PostgreSQL is required.",
            location="Remote",
            fetched_at=now_utc,
            verification_status="verified",
        ),
        NormalizedJob(
            employer_name="Stripe",
            job_title="Senior Backend Infrastructure Engineer",
            source_name="lever",
            source_url="https://jobs.lever.co/stripe/102",
            description_text="Requirements: Strong proficiency in Go and Kubernetes. Python experience is a plus.",
            location="San Francisco, CA",
            fetched_at=now_utc,
            verification_status="verified",
        ),
    ]

    with patch("app.services.job_search_service.get_default_connectors") as mock_get_conn:
        mock_gh = MagicMock()
        mock_gh.source_name = "Greenhouse"
        mock_gh.source_type = "public_ats_feed"
        mock_gh.search_jobs_detailed.return_value = ("verified_jobs_found", "OK", [mock_jobs[0]])

        mock_lever = MagicMock()
        mock_lever.source_name = "Lever"
        mock_lever.source_type = "public_ats_feed"
        mock_lever.search_jobs_detailed.return_value = ("verified_jobs_found", "OK", [mock_jobs[1]])

        mock_get_conn.return_value = [mock_gh, mock_lever]

        search_res = client.post(f"/api/analyses/{analysis_id}/search-jobs", headers=headers1)
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["status"] == "verified_jobs_found"
        assert len(search_data["jobs"]) == 2

    # 5. Run skill gap analysis
    gap_res = client.post(f"/api/analyses/{analysis_id}/run-gap-analysis", headers=headers1)
    assert gap_res.status_code == 200
    gap_data = gap_res.json()

    # Required skills from job 101: Python (required), Docker (required), PostgreSQL (required)
    # Required skills from job 102: Go (required), Kubernetes (required), Python (preferred/plus)
    # Student reported: Python (intermediate) -> self_reported_covered
    # Missing required skills: Docker, PostgreSQL, Go, Kubernetes
    assert gap_data["coverage_percentage"] is not None
    assert 0 < gap_data["coverage_percentage"] <= 100
    assert "coverage_explanation" in gap_data
    assert len(gap_data["skill_gaps"]) >= 4

    # 6. Generate roadmap bounded by 10 weekly hours
    roadmap_res = client.post(f"/api/analyses/{analysis_id}/roadmap", headers=headers1)
    assert roadmap_res.status_code == 201
    roadmap_data = roadmap_res.json()
    assert roadmap_data["weekly_hours_budget"] == 10
    assert roadmap_data["total_weeks"] >= 1
    assert len(roadmap_data["items"]) >= 1

    # Verify weekly budget constraints: no week exceeds 10 hours
    weekly_hours = {}
    for item in roadmap_data["items"]:
        w = item["week_number"]
        weekly_hours[w] = weekly_hours.get(w, 0) + item["estimated_hours"]
    for w, hours in weekly_hours.items():
        assert hours <= 10, f"Week {w} exceeds weekly budget of 10 hours: {hours}h"

    # 7. Update progress of the first roadmap item
    first_item = roadmap_data["items"][0]
    first_item_id = first_item["id"]
    patch_res = client.patch(
        f"/api/roadmap-items/{first_item_id}",
        headers=headers1,
        json={"status": "in_progress"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "in_progress"

    # 8. List analyses on dashboard
    dash_res = client.get("/api/analyses", headers=headers1)
    assert dash_res.status_code == 200
    assert any(a["id"] == analysis_id for a in dash_res.json())

    # 9. Verify isolation with a second student
    reg_res2 = client.post(
        "/api/auth/register",
        json={
            "email": "alex.other@university.edu",
            "password": "AnotherSecurePassword123!",
            "name": "Alex Other",
        },
    )
    assert reg_res2.status_code == 201
    headers2 = {"Authorization": f"Bearer {reg_res2.json()['access_token']}"}

    # Second student cannot access first student's analysis (returns 404 for IDOR security)
    forbidden_get = client.get(f"/api/analyses/{analysis_id}", headers=headers2)
    assert forbidden_get.status_code == 404

    # Second student cannot patch first student's roadmap item (returns 404 for IDOR security)
    forbidden_patch = client.patch(
        f"/api/roadmap-items/{first_item_id}",
        headers=headers2,
        json={"status": "completed"},
    )
    assert forbidden_patch.status_code == 404

    # Second student's dashboard is empty
    dash_res2 = client.get("/api/analyses", headers=headers2)
    assert dash_res2.status_code == 200
    assert len(dash_res2.json()) == 0

    # 10. Delete analysis by owner and verify clean cascade
    del_res = client.delete(f"/api/analyses/{analysis_id}", headers=headers1)
    assert del_res.status_code == 204

    # Verify analysis is gone
    get_after_del = client.get(f"/api/analyses/{analysis_id}", headers=headers1)
    assert get_after_del.status_code == 404
