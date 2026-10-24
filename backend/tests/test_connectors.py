from unittest.mock import MagicMock
import httpx
import pytest

from app.connectors.greenhouse import (
    GreenhouseConnector,
    clean_html_description,
    calculate_role_relevance,
)
from app.models.job_snapshot import JobSnapshot


# Sample mock fixture for Greenhouse API response
MOCK_GREENHOUSE_RESPONSE = {
    "jobs": [
        {
            "id": 1001,
            "title": "Senior Backend Engineer",
            "absolute_url": "https://boards.greenhouse.io/stripe/jobs/1001",
            "location": {"name": "San Francisco, CA / Remote"},
            "updated_at": "2026-04-10T14:30:00Z",
            "content": (
                "&lt;h3&gt;About the Role&lt;/h3&gt;&lt;p&gt;We are looking for a Senior Backend Engineer.&lt;/p&gt;"
                "&lt;ul&gt;&lt;li&gt;5+ years experience with Python and SQL.&lt;/li&gt;&lt;/ul&gt;"
            ),
        },
        {
            "id": 1002,
            "title": "Account Executive",
            "absolute_url": "https://boards.greenhouse.io/stripe/jobs/1002",
            "location": {"name": "New York, NY"},
            "updated_at": "2026-04-09T10:00:00Z",
            "content": "&lt;p&gt;Drive enterprise sales across our portfolio.&lt;/p&gt;",
        },
    ]
}


def test_html_cleaning():
    """Verifies that clean_html_description removes HTML tags and decodes entities properly."""
    raw = "&lt;p&gt;Proficiency in &amp;amp; knowledge of &lt;b&gt;Python&lt;/b&gt;.&lt;/p&gt;&lt;script&gt;alert(1)&lt;/script&gt;"
    cleaned = clean_html_description(raw)
    assert "<p>" not in cleaned
    assert "<b>" not in cleaned
    assert "<script>" not in cleaned
    assert "alert(1)" not in cleaned
    assert "Proficiency in & knowledge of Python." in cleaned


def test_calculate_role_relevance():
    """Verifies the token and phrase relevance calculation between target roles and job titles."""
    is_rel, _ = calculate_role_relevance("Senior Data Analyst", "Data Analyst")
    assert is_rel is True

    is_rel, _ = calculate_role_relevance("Backend Software Engineer", "Backend Engineer")
    assert is_rel is True

    is_rel, _ = calculate_role_relevance("Front-End Developer", "Data Scientist")
    assert is_rel is False

    is_rel, _ = calculate_role_relevance("Senior Recruiter", "DevOps Engineer")
    assert is_rel is False


def test_greenhouse_connector_success_with_mock():
    """Verifies that GreenhouseConnector parses valid job feeds and extracts relevant postings."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_GREENHOUSE_RESPONSE
    mock_client.get.return_value = mock_response

    connector = GreenhouseConnector(client=mock_client)
    status_code, msg, jobs = connector.search_jobs_detailed("Stripe", "Backend Engineer")

    assert status_code == "verified_jobs_found"
    assert len(jobs) == 1
    job = jobs[0]
    assert job.employer_name == "Stripe"
    assert job.job_title == "Senior Backend Engineer"
    assert "About the Role" in job.description_text
    assert "5+ years experience with Python and SQL." in job.description_text
    assert job.source_name == "Greenhouse"
    assert job.source_type == "public_ats_feed"
    assert job.location == "San Francisco, CA / Remote"
    assert job.content_hash is not None
    assert job.verification_status == "verified"


def test_greenhouse_connector_company_not_verified_404():
    """Verifies that an unknown company returning 404 sets company_not_verified status."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_client.get.return_value = mock_response

    connector = GreenhouseConnector(client=mock_client)
    status_code, msg, jobs = connector.search_jobs_detailed("UnknownCompany99", "Software Engineer")

    assert status_code == "company_not_verified"
    assert len(jobs) == 0
    assert "no public greenhouse job board could be verified" in msg.lower()


def test_greenhouse_connector_no_matching_jobs():
    """Verifies that when positions exist but none match the role, no_matching_jobs is returned."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_GREENHOUSE_RESPONSE
    mock_client.get.return_value = mock_response

    connector = GreenhouseConnector(client=mock_client)
    status_code, msg, jobs = connector.search_jobs_detailed("Stripe", "Cloud Security Architect")

    assert status_code == "no_matching_jobs"
    assert len(jobs) == 0
    assert "none matched" in msg.lower()


def test_greenhouse_connector_timeout_handling():
    """Verifies that network timeouts are caught and reported as source_unavailable."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.side_effect = httpx.TimeoutException("Connection timed out")

    connector = GreenhouseConnector(client=mock_client)
    status_code, msg, jobs = connector.search_jobs_detailed("Stripe", "Backend Engineer")

    assert status_code == "source_unavailable"
    assert len(jobs) == 0
    assert "timed out" in msg.lower()


def test_greenhouse_connector_upstream_500_handling():
    """Verifies that upstream 5xx errors return source_unavailable status."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_client.get.side_effect = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=mock_response)

    connector = GreenhouseConnector(client=mock_client)
    status_code, msg, jobs = connector.search_jobs_detailed("Stripe", "Backend Engineer")

    assert status_code == "source_unavailable"
    assert len(jobs) == 0


def test_api_search_jobs_integration(client, db_session, monkeypatch):
    """
    Integration test verifying POST /api/analyses/{id}/search-jobs
    orchestrates the search, persists JobSnapshot records, and updates analysis status.
    """
    # 1. Register and get token
    reg = client.post(
        "/api/auth/register",
        json={"name": "Dev User", "email": "dev.user@example.com", "password": "Password123!"},
    )
    assert reg.status_code == 201
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}

    # 2. Create analysis
    analysis_res = client.post(
        "/api/analyses",
        json={"company_name": "Stripe", "target_role": "Backend Engineer", "weekly_hours": 10},
        headers=headers,
    )
    analysis_id = analysis_res.json()["id"]

    # 3. Mock GreenhouseConnector to return valid posting
    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_GREENHOUSE_RESPONSE
    mock_client.get.return_value = mock_response

    monkeypatch.setattr(
        "app.connectors.greenhouse.GreenhouseConnector._get_client",
        lambda self: mock_client,
    )

    # Mock LeverConnector as well to prevent external HTTP calls during automated tests
    mock_lever_client = MagicMock(spec=httpx.Client)
    mock_lever_res = MagicMock(spec=httpx.Response)
    mock_lever_res.status_code = 404
    mock_lever_client.get.return_value = mock_lever_res
    monkeypatch.setattr(
        "app.connectors.lever.LeverConnector._get_client",
        lambda self: mock_lever_client,
    )

    # 4. Trigger search-jobs endpoint
    search_res = client.post(f"/api/analyses/{analysis_id}/search-jobs", headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["status"] == "verified_jobs_found"
    assert len(search_data["jobs"]) == 1
    assert search_data["jobs"][0]["job_title"] == "Senior Backend Engineer"

    # 5. Verify snapshot in SQLite database
    snapshots = db_session.query(JobSnapshot).filter(JobSnapshot.analysis_id == analysis_id).all()
    assert len(snapshots) == 1
    assert snapshots[0].employer_name == "Stripe"
    assert snapshots[0].job_title == "Senior Backend Engineer"

    # 6. Verify GET /api/analyses/{id} now returns job_snapshots
    get_res = client.get(f"/api/analyses/{analysis_id}", headers=headers)
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["status"] == "verified_jobs_found"
    assert len(detail["job_snapshots"]) == 1


def test_api_search_jobs_ownership_check(client):
    """Verifies that User B cannot trigger job search on User A's analysis."""
    reg_a = client.post(
        "/api/auth/register",
        json={"name": "User A", "email": "user.a@test.com", "password": "Password123!"},
    )
    headers_a = {"Authorization": f"Bearer {reg_a.json()['access_token']}"}

    reg_b = client.post(
        "/api/auth/register",
        json={"name": "User B", "email": "user.b@test.com", "password": "Password123!"},
    )
    headers_b = {"Authorization": f"Bearer {reg_b.json()['access_token']}"}

    # User A creates analysis
    create_res = client.post(
        "/api/analyses",
        json={"company_name": "Stripe", "target_role": "Backend Engineer", "weekly_hours": 10},
        headers=headers_a,
    )
    analysis_id = create_res.json()["id"]

    # User B attempts to run search-jobs
    bad_res = client.post(f"/api/analyses/{analysis_id}/search-jobs", headers=headers_b)
    assert bad_res.status_code == 404
