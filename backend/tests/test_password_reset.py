from datetime import datetime, timezone, timedelta
import hashlib
from app.models.user import User
from app.models.password_reset import PasswordResetToken


def test_forgot_password_and_reset_flow(client, db_session):
    """Verifies end-to-end password reset flow including single-use token and new password login."""
    # 1. Register student
    reg = client.post(
        "/api/auth/register",
        json={"name": "Reset Student", "email": "reset.student@university.edu", "password": "OldPassword123!"},
    )
    assert reg.status_code == 201

    # 2. Request forgot-password
    forgot_res = client.post(
        "/api/auth/forgot-password",
        json={"email": "reset.student@university.edu"},
    )
    assert forgot_res.status_code == 200
    forgot_data = forgot_res.json()
    assert "If an account exists for this email address" in forgot_data["message"]
    # In local testing without SMTP, token is provided in response for verification
    raw_token = forgot_data["reset_token"]
    assert raw_token is not None

    # Verify token is stored as SHA-256 hash in DB, never plaintext
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    db_token = db_session.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()
    assert db_token is not None
    assert db_token.is_used is False

    # 3. Reset password with new matching password
    reset_res = client.post(
        "/api/auth/reset-password",
        json={
            "token": raw_token,
            "new_password": "BrandNewPassword123!",
            "confirm_password": "BrandNewPassword123!",
        },
    )
    assert reset_res.status_code == 200
    assert reset_res.json()["success"] is True

    # 4. Old password should now fail
    old_login = client.post(
        "/api/auth/login",
        json={"email": "reset.student@university.edu", "password": "OldPassword123!"},
    )
    assert old_login.status_code == 401

    # 5. New password should successfully authenticate
    new_login = client.post(
        "/api/auth/login",
        json={"email": "reset.student@university.edu", "password": "BrandNewPassword123!"},
    )
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()

    # 6. Reusing the same reset token must be rejected
    reuse_res = client.post(
        "/api/auth/reset-password",
        json={
            "token": raw_token,
            "new_password": "AnotherPassword123!",
            "confirm_password": "AnotherPassword123!",
        },
    )
    assert reuse_res.status_code == 400
    assert "already used" in reuse_res.json()["detail"].lower()


def test_forgot_password_neutral_response_for_nonexistent_email(client):
    """Verifies that non-existent emails receive the exact same neutral response (no email enumeration)."""
    res = client.post(
        "/api/auth/forgot-password",
        json={"email": "nonexistent.student.999@university.edu"},
    )
    assert res.status_code == 200
    assert "If an account exists for this email address" in res.json()["message"]
    assert res.json()["reset_token"] is None


def test_reset_password_validation_mismatched_passwords(client):
    """Verifies that mismatched passwords during reset are rejected with 422."""
    res = client.post(
        "/api/auth/reset-password",
        json={
            "token": "valid_looking_token_1234567890",
            "new_password": "FirstPassword123!",
            "confirm_password": "SecondPassword999!",
        },
    )
    assert res.status_code == 422
    assert "do not match" in res.text.lower()


def test_reset_password_expired_token(client, db_session):
    """Verifies that an expired reset token is rejected with 400."""
    user = User(name="Expired Tester", email="expired@university.edu", password_hash="dummy")
    db_session.add(user)
    db_session.commit()

    raw_token = "expired_raw_token_test_1234567890"
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    # Create token expired 10 minutes ago
    expired_token = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(minutes=10),
        is_used=False,
    )
    db_session.add(expired_token)
    db_session.commit()

    res = client.post(
        "/api/auth/reset-password",
        json={
            "token": raw_token,
            "new_password": "NewSecurePassword123!",
            "confirm_password": "NewSecurePassword123!",
        },
    )
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()
