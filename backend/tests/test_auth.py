from datetime import timedelta
from app.models.user import User
from app.security.jwt_handler import create_access_token


def test_register_success(client, db_session):
    """Verifies that a student can successfully register and receive an access token."""
    payload = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "StrongPassword123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == "jane.doe@example.com"
    assert data["user"]["name"] == "Jane Doe"
    assert "id" in data["user"]

    # Security check: Password hash must never leak in API responses
    assert "password" not in data["user"]
    assert "password_hash" not in data["user"]

    # Verify password was hashed with Argon2 in the database
    db_user = db_session.query(User).filter(User.email == "jane.doe@example.com").first()
    assert db_user is not None
    assert db_user.password_hash.startswith("$argon2id$")
    assert db_user.password_hash != "StrongPassword123!"


def test_register_duplicate_email(client):
    """Verifies that registering with an already existing email is rejected."""
    payload = {
        "name": "Alex Smith",
        "email": "alex@example.com",
        "password": "Password1234!",
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt to register with identical email in different case
    res2 = client.post(
        "/api/auth/register",
        json={
            "name": "Alexander",
            "email": "ALEX@example.com",
            "password": "AnotherPassword567!",
        },
    )
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()


def test_register_validation_errors(client):
    """Verifies input validation rules for name, email, and password length."""
    # Password too short (< 8 chars)
    res_short_pwd = client.post(
        "/api/auth/register",
        json={"name": "Bob", "email": "bob@example.com", "password": "short"},
    )
    assert res_short_pwd.status_code == 422

    # Name too short / blank
    res_blank_name = client.post(
        "/api/auth/register",
        json={"name": "   ", "email": "bob@example.com", "password": "ValidPassword123"},
    )
    assert res_blank_name.status_code == 422

    # Invalid email format
    res_bad_email = client.post(
        "/api/auth/register",
        json={"name": "Bob Vance", "email": "not-an-email", "password": "ValidPassword123"},
    )
    assert res_bad_email.status_code == 422


def test_login_success(client):
    """Verifies that a registered student can log in with valid credentials."""
    client.post(
        "/api/auth/register",
        json={"name": "Sarah Connor", "email": "sarah@resistance.org", "password": "SkynetPassword2026!"},
    )

    login_res = client.post(
        "/api/auth/login",
        json={"email": "sarah@resistance.org", "password": "SkynetPassword2026!"},
    )
    assert login_res.status_code == 200
    data = login_res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "sarah@resistance.org"


def test_login_wrong_password(client):
    """Verifies that login fails when given an incorrect password."""
    client.post(
        "/api/auth/register",
        json={"name": "John Connor", "email": "john@resistance.org", "password": "ValidPassword1!"},
    )

    bad_login = client.post(
        "/api/auth/login",
        json={"email": "john@resistance.org", "password": "WrongPassword!"},
    )
    assert bad_login.status_code == 401
    assert "invalid email or password" in bad_login.json()["detail"].lower()


def test_login_nonexistent_email(client):
    """Verifies that login fails for an unregistered email."""
    response = client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "AnyPassword123!"},
    )
    assert response.status_code == 401


def test_get_current_user_me_authenticated(client):
    """Verifies that an authenticated request to /api/auth/me returns the user profile."""
    reg_res = client.post(
        "/api/auth/register",
        json={"name": "Ellen Ripley", "email": "ripley@weyland.com", "password": "Nostromo1979!"},
    )
    token = reg_res.json()["access_token"]

    me_res = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["name"] == "Ellen Ripley"
    assert user_data["email"] == "ripley@weyland.com"
    assert "password_hash" not in user_data


def test_get_current_user_me_unauthenticated(client):
    """Verifies that unauthenticated access to /api/auth/me is rejected with 401."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_current_user_me_invalid_token(client):
    """Verifies that requests with malformed tokens are rejected."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer malformed.invalid.token"},
    )
    assert response.status_code == 401


def test_get_current_user_me_expired_token(client, db_session):
    """Verifies that expired JWT tokens are rejected with 401."""
    # Create user in database
    user = User(name="Timely User", email="timely@example.com", password_hash="dummy")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Generate token that expired 10 minutes ago
    expired_token = create_access_token(
        subject=user.id,
        expires_delta=timedelta(minutes=-10),
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()
