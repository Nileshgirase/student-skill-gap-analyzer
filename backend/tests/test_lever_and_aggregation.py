from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock
import httpx
import pytest

from app.connectors.lever import LeverConnector
from app.connectors.base import NormalizedJob
from app.services.job_search_service import (
    execute_job_search,
    evaluate_posting_freshness,
)
from app.models.analysis import Analysis
from app.models.job_snapshot import JobSnapshot

# Mock Lever API JSON response fixture
MOCK_LEVER_RESPONSE = [
    {
        "id": "lever-job-001",
        "text": "Full Stack Engineer",
        "hostedUrl": "https://jobs.lever.co/netflix/lever-job-001",
        "categories": {
            "location": "Los Gatos, CA / Remote",
            "commitment": "Full-time",
            "team": "Engineering",
        },
        "descriptionPlain": "We are seeking a Full Stack Engineer to build core web interfaces.",
        "lists": [
            {
                "text": "Requirements",
                "content": "&lt;li&gt;Proficiency in React and Python.&lt;/li&gt;&lt;li&gt;Experience with SQL.&lt;/li&gt;",
            }
        ],
        "createdAt": int((datetime.now(timezone.utc) - timedelta(days=5)).timestamp() * 1000),
    },
    {
        "id": "lever-job-002",
        "text": "Senior Legal Counsel",
        "hostedUrl": "https://jobs.lever.co/netflix/lever-job-002",
        "categories": {"location": "Los Angeles, CA"},
        "descriptionPlain": "Advise on international content licensing and transactions.",
        "lists": [],
        "createdAt": int((datetime.now(timezone.utc) - timedelta(days=10)).timestamp() * 1000),
    },
]


def test_lever_connector_success_with_mock():
    """Verifies that LeverConnector queries and parses valid job postings."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_LEVER_RESPONSE
    mock_client.get.return_value = mock_response

    connector = LeverConnector(client=mock_client)
    status_code, msg, jobs = connector.search_jobs_detailed("Netflix", "Full Stack Engineer")

    assert status_code == "verified_jobs_found"
    assert len(jobs) == 1
    job = jobs[0]
    assert job.employer_name == "Netflix"
    assert job.job_title == "Full Stack Engineer"
    assert job.source_name == "Lever"
    assert "Requirements:" in job.description_text
    assert "Proficiency in React and Python." in job.description_text
    assert job.location == "Los Gatos, CA / Remote"
    assert job.employment_type == "Full-time"
    assert job.posted_at is not None


def test_lever_connector_404_handling():
    """Verifies that an unlisted company returning 404 sets company_not_verified."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_client.get.return_value = mock_response

    connector = LeverConnector(client=mock_client)
    status_code, msg, jobs = connector.search_jobs_detailed("NotOnLeverCorp", "Developer")

    assert status_code == "company_not_verified"
    assert len(jobs) == 0


def test_lever_connector_timeout_handling():
    """Verifies that timeouts on Lever return source_unavailable."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.get.side_effect = httpx.TimeoutException("Lever connection timed out")

    connector = LeverConnector(client=mock_client)
    status_code, msg, jobs = connector.search_jobs_detailed("Netflix", "Developer")

    assert status_code == "source_unavailable"
    assert len(jobs) == 0


def test_freshness_policy_evaluation():
    """Verifies that postings older than threshold days are flagged as stale."""
    now = datetime.now(timezone.utc)

    # 1. Fresh posting: 5 days old (threshold is 30)
    fresh_date = now - timedelta(days=5)
    is_stale, note = evaluate_posting_freshness(fresh_date)
    assert is_stale is False
    assert "Fresh" in note

    # 2. Stale posting: 45 days old (threshold is 30)
    stale_date = now - timedelta(days=45)
    is_stale, note = evaluate_posting_freshness(stale_date)
    assert is_stale is True
    assert "exceeds freshness policy" in note

    # 3. None date
    is_stale, note = evaluate_posting_freshness(None)
    assert is_stale is False
    assert note is None


def test_multi_source_deduplication(db_session):
    """
    Verifies that when multiple connectors return identical job postings (same URL/content),
    the search service deduplicates them before storing snapshots.
    """
    analysis = Analysis(
        user_id=1,
        company_name="MultiSourceCorp",
        target_role="Software Engineer",
        weekly_hours=10,
        status="pending",
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    now = datetime.now(timezone.utc)
    # Connector A returns Job 1
    job1 = NormalizedJob(
        employer_name="MultiSourceCorp",
        job_title="Software Engineer",
        source_name="Greenhouse",
        source_url="https://boards.greenhouse.io/corp/1",
        description_text="Same description across platforms.",
        content_hash="hash123",
        fetched_at=now,
        verification_status="verified",
    )

    # Connector B returns identical Job 1 (same content hash)
    job2 = NormalizedJob(
        employer_name="MultiSourceCorp",
        job_title="Software Engineer",
        source_name="Lever",
        source_url="https://jobs.lever.co/corp/1",
        description_text="Same description across platforms.",
        content_hash="hash123",  # Identical hash
        fetched_at=now,
        verification_status="verified",
    )

    mock_conn1 = MagicMock()
    mock_conn1.source_name = "Greenhouse"
    mock_conn1.search_jobs_detailed.return_value = ("verified_jobs_found", "ok", [job1])

    mock_conn2 = MagicMock()
    mock_conn2.source_name = "Lever"
    mock_conn2.search_jobs_detailed.return_value = ("verified_jobs_found", "ok", [job2])

    status_code, msg, snapshots = execute_job_search(
        analysis=analysis,
        db=db_session,
        connectors=[mock_conn1, mock_conn2],
    )

    assert status_code == "verified_jobs_found"
    # Deduplication must reduce 2 identical items to 1 snapshot
    assert len(snapshots) == 1
    assert snapshots[0].content_hash == "hash123"


def test_multi_source_aggregation_graceful_failure(db_session):
    """
    Verifies that if one source times out, the search service still succeeds
    using valid postings from the remaining available source(s).
    """
    analysis = Analysis(
        user_id=1,
        company_name="ResilientCorp",
        target_role="Data Engineer",
        weekly_hours=15,
        status="pending",
    )
    db_session.add(analysis)
    db_session.commit()
    db_session.refresh(analysis)

    # Connector 1 fails with source_unavailable
    mock_conn_fail = MagicMock()
    mock_conn_fail.source_name = "Greenhouse"
    mock_conn_fail.search_jobs_detailed.return_value = ("source_unavailable", "Timeout", [])

    # Connector 2 succeeds with Lever posting
    now = datetime.now(timezone.utc)
    valid_job = NormalizedJob(
        employer_name="ResilientCorp",
        job_title="Data Engineer",
        source_name="Lever",
        source_url="https://jobs.lever.co/resilient/10",
        description_text="Data engineering description.",
        content_hash="hash999",
        fetched_at=now,
        verification_status="verified",
    )
    mock_conn_success = MagicMock()
    mock_conn_success.source_name = "Lever"
    mock_conn_success.search_jobs_detailed.return_value = ("verified_jobs_found", "ok", [valid_job])

    status_code, msg, snapshots = execute_job_search(
        analysis=analysis,
        db=db_session,
        connectors=[mock_conn_fail, mock_conn_success],
    )

    # The search must succeed with the valid posting from Lever
    assert status_code == "verified_jobs_found"
    assert len(snapshots) == 1
    assert snapshots[0].source_name == "Lever"
    assert snapshots[0].job_title == "Data Engineer"
