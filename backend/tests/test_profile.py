import pytest


def test_get_profile_creates_default_and_returns_data(client):
    """Verifies that an authenticated student can retrieve their profile with default values."""
    # 1. Register student
    reg = client.post(
        "/api/auth/register",
        json={"name": "Alice Profile", "email": "alice.profile@university.edu", "password": "SecurePassword123!"},
    )
    assert reg.status_code == 201
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    # 2. Get profile
    res = client.get("/api/profile", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Alice Profile"
    assert data["email"] == "alice.profile@university.edu"
    assert data["weekly_study_hours"] == 10
    assert data["current_skills"] == []


def test_update_profile_and_persistence(client):
    """Verifies that updating personal and academic fields updates the database and persists."""
    reg = client.post(
        "/api/auth/register",
        json={"name": "Bob Student", "email": "bob.student@university.edu", "password": "SecurePassword123!"},
    )
    assert reg.status_code == 201
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    update_payload = {
        "name": "Bob Updated Name",
        "mobile_number": "+1 (555) 234-5678",
        "college_name": "Stanford University",
        "degree": "B.S. in Computer Science",
        "specialization": "Artificial Intelligence",
        "graduation_year": 2027,
        "weekly_study_hours": 15,
        "avatar_url": "avatar-3",
        "bio": "Aspiring Machine Learning Engineer dedicated to learning Python and Data Structures.",
        "current_skills": ["Python", "SQL", "Git"],
    }
    update_res = client.put("/api/profile", headers=headers, json=update_payload)
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["name"] == "Bob Updated Name"
    assert updated["college_name"] == "Stanford University"
    assert updated["weekly_study_hours"] == 15
    assert updated["current_skills"] == ["Python", "SQL", "Git"]

    # Verify persistence by calling GET
    get_res = client.get("/api/profile", headers=headers)
    assert get_res.status_code == 200
    fetched = get_res.json()
    assert fetched["name"] == "Bob Updated Name"
    assert fetched["mobile_number"] == "+1 (555) 234-5678"
    assert fetched["degree"] == "B.S. in Computer Science"
    assert fetched["graduation_year"] == 2027


def test_profile_validation_rejects_invalid_inputs(client):
    """Verifies input validation on mobile number format and graduation year."""
    reg = client.post(
        "/api/auth/register",
        json={"name": "Charlie Test", "email": "charlie@university.edu", "password": "SecurePassword123!"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    # Invalid mobile number with letters
    res1 = client.put(
        "/api/profile",
        headers=headers,
        json={"name": "Charlie", "mobile_number": "not-a-valid-phone-number-xyz"},
    )
    assert res1.status_code == 422

    # Invalid graduation year (too far in future)
    res2 = client.put(
        "/api/profile",
        headers=headers,
        json={"name": "Charlie", "graduation_year": 2999},
    )
    assert res2.status_code == 422


def test_unauthenticated_profile_access_rejected(client):
    """Verifies that accessing or updating profiles without a token returns 401."""
    res1 = client.get("/api/profile")
    assert res1.status_code == 401

    res2 = client.put("/api/profile", json={"name": "Hacker"})
    assert res2.status_code == 401
