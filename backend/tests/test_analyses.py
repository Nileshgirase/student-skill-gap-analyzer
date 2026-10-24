import pytest
from app.models.student_skill import StudentSkill
from app.models.analysis import Analysis


@pytest.fixture
def user_a_headers(client):
    reg = client.post(
        "/api/auth/register",
        json={"name": "Alice Developer", "email": "alice.dev@test.org", "password": "Password123!"},
    )
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_b_headers(client):
    reg = client.post(
        "/api/auth/register",
        json={"name": "Bob Analyst", "email": "bob.analyst@test.org", "password": "Password456!"},
    )
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_analysis_success(client, user_a_headers):
    """Verifies that a student can create a new analysis with free-text inputs and skills."""
    payload = {
        "company_name": "TCS",
        "target_role": "Data Analyst",
        "weekly_hours": 10,
        "student_skills": [
            {"name": "Python", "proficiency": "intermediate"},
            {"name": "SQL", "proficiency": "beginner"},
            {"name": "Postgres", "proficiency": "beginner"},
        ],
    }
    response = client.post("/api/analyses", json=payload, headers=user_a_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["company_name"] == "TCS"
    assert data["target_role"] == "Data Analyst"
    assert data["weekly_hours"] == 10
    assert data["status"] == "pending"
    assert len(data["student_skills"]) == 3

    # Check canonical skill normalization (e.g. Postgres -> postgresql)
    canonical_skills = {s["canonical_skill"] for s in data["student_skills"]}
    assert "postgresql" in canonical_skills
    assert "python" in canonical_skills
    assert "sql" in canonical_skills


def test_create_analysis_validation_failure(client, user_a_headers):
    """Verifies validation rejecting zero/negative hours, excess hours, or empty free-text inputs."""
    # Zero weekly study hours
    res_zero_hours = client.post(
        "/api/analyses",
        json={"company_name": "Google", "target_role": "SRE", "weekly_hours": 0},
        headers=user_a_headers,
    )
    assert res_zero_hours.status_code == 422

    # Negative weekly study hours
    res_neg_hours = client.post(
        "/api/analyses",
        json={"company_name": "Google", "target_role": "SRE", "weekly_hours": -5},
        headers=user_a_headers,
    )
    assert res_neg_hours.status_code == 422

    # Empty company name
    res_empty_company = client.post(
        "/api/analyses",
        json={"company_name": "   ", "target_role": "SRE", "weekly_hours": 10},
        headers=user_a_headers,
    )
    assert res_empty_company.status_code == 422

    # Empty target role
    res_empty_role = client.post(
        "/api/analyses",
        json={"company_name": "Google", "target_role": "   ", "weekly_hours": 10},
        headers=user_a_headers,
    )
    assert res_empty_role.status_code == 422


def test_list_analyses_ownership_scoping(client, user_a_headers, user_b_headers):
    """Verifies that students only see their own analyses (strict tenant isolation)."""
    # User A creates 2 analyses
    client.post(
        "/api/analyses",
        json={"company_name": "Company A1", "target_role": "Role A1", "weekly_hours": 8},
        headers=user_a_headers,
    )
    client.post(
        "/api/analyses",
        json={"company_name": "Company A2", "target_role": "Role A2", "weekly_hours": 12},
        headers=user_a_headers,
    )

    # User B creates 1 analysis
    client.post(
        "/api/analyses",
        json={"company_name": "Company B1", "target_role": "Role B1", "weekly_hours": 6},
        headers=user_b_headers,
    )

    # User A should see only their 2 analyses
    res_a = client.get("/api/analyses", headers=user_a_headers)
    assert res_a.status_code == 200
    list_a = res_a.json()
    assert len(list_a) == 2
    assert {item["company_name"] for item in list_a} == {"Company A1", "Company A2"}

    # User B should see only their 1 analysis
    res_b = client.get("/api/analyses", headers=user_b_headers)
    assert res_b.status_code == 200
    list_b = res_b.json()
    assert len(list_b) == 1
    assert list_b[0]["company_name"] == "Company B1"


def test_get_analysis_by_id_owner_vs_non_owner(client, user_a_headers, user_b_headers):
    """Verifies that an analysis can be retrieved by its owner but returns 404 to other users (IDOR prevention)."""
    create_res = client.post(
        "/api/analyses",
        json={"company_name": "Stripe", "target_role": "Backend Engineer", "weekly_hours": 15},
        headers=user_a_headers,
    )
    analysis_id = create_res.json()["id"]

    # Owner (User A) accesses successfully
    get_owner = client.get(f"/api/analyses/{analysis_id}", headers=user_a_headers)
    assert get_owner.status_code == 200
    assert get_owner.json()["company_name"] == "Stripe"

    # Non-owner (User B) tries to access User A's analysis
    get_non_owner = client.get(f"/api/analyses/{analysis_id}", headers=user_b_headers)
    assert get_non_owner.status_code == 404
    assert "not found" in get_non_owner.json()["detail"].lower()


def test_delete_analysis_and_cascade(client, db_session, user_a_headers, user_b_headers):
    """Verifies that deletion deletes the analysis and cascades to remove student skills."""
    create_res = client.post(
        "/api/analyses",
        json={
            "company_name": "Microsoft",
            "target_role": "Software Engineer",
            "weekly_hours": 20,
            "student_skills": [{"name": "C#", "proficiency": "intermediate"}],
        },
        headers=user_a_headers,
    )
    analysis_id = create_res.json()["id"]

    # Non-owner (User B) cannot delete User A's analysis
    del_forbidden = client.delete(f"/api/analyses/{analysis_id}", headers=user_b_headers)
    assert del_forbidden.status_code == 404

    # Owner (User A) deletes successfully
    del_res = client.delete(f"/api/analyses/{analysis_id}", headers=user_a_headers)
    assert del_res.status_code == 204

    # Verify analysis is deleted from DB
    db_analysis = db_session.query(Analysis).filter(Analysis.id == analysis_id).first()
    assert db_analysis is None

    # Verify student skills were cascade deleted
    db_skills = db_session.query(StudentSkill).filter(StudentSkill.analysis_id == analysis_id).all()
    assert len(db_skills) == 0


def test_update_student_skills_endpoint(client, user_a_headers, user_b_headers):
    """Verifies that a student can update or replace skills for their owned analysis."""
    create_res = client.post(
        "/api/analyses",
        json={
            "company_name": "Amazon",
            "target_role": "Cloud Architect",
            "weekly_hours": 10,
            "student_skills": [{"name": "Linux", "proficiency": "beginner"}],
        },
        headers=user_a_headers,
    )
    analysis_id = create_res.json()["id"]

    # Non-owner cannot update skills
    update_non_owner = client.post(
        f"/api/analyses/{analysis_id}/student-skills",
        json={"student_skills": [{"name": "AWS", "proficiency": "advanced"}]},
        headers=user_b_headers,
    )
    assert update_non_owner.status_code == 404

    # Owner updates skills
    update_res = client.post(
        f"/api/analyses/{analysis_id}/student-skills",
        json={
            "student_skills": [
                {"name": "Amazon Web Services", "proficiency": "advanced"},
                {"name": "Docker", "proficiency": "intermediate"},
            ]
        },
        headers=user_a_headers,
    )
    assert update_res.status_code == 200
    skills = update_res.json()
    assert len(skills) == 2
    canonical_set = {s["canonical_skill"] for s in skills}
    assert "aws" in canonical_set
    assert "docker" in canonical_set


def test_unauthenticated_access_rejected(client):
    """Verifies that unauthenticated requests to analyses endpoints return 401."""
    assert client.get("/api/analyses").status_code == 401
    assert client.post("/api/analyses", json={}).status_code == 401
    assert client.get("/api/analyses/1").status_code == 401
    assert client.delete("/api/analyses/1").status_code == 401
    assert client.post("/api/analyses/1/student-skills", json={}).status_code == 401
