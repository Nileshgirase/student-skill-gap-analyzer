from unittest.mock import patch
from app.database import check_db_connection


def test_root_endpoint(client):
    """Verifies that the API root endpoint responds with basic service details."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["docs_url"] == "/docs"
    assert "app_name" in data


def test_health_check_healthy(client):
    """Verifies that /api/health reports healthy when the database is reachable."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "timestamp" in data
    assert data["environment"] == "development"


def test_database_connection_check(db_session):
    """Directly verifies the database connectivity check function."""
    assert check_db_connection(db_session) is True


def test_health_check_degraded_when_db_down(client):
    """Verifies that /api/health gracefully returns HTTP 503 and degraded when DB is unreachable."""
    with patch("app.routes.health.check_db_connection", return_value=False):
        response = client.get("/api/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"] == "disconnected"
