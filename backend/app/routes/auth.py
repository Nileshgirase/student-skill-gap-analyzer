import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from app.schemas.password_reset import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
)
from app.security.password import hash_password, verify_password
from app.security.jwt_handler import create_access_token
from app.security.dependencies import get_current_user
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register New Student",
    description="Registers a new student user, hashes password with Argon2, and returns a JWT access token.",
)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    # Check for existing user with identical email
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Hash password securely using Argon2id
    hashed_pwd = hash_password(payload.password)

    new_user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hashed_pwd,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(subject=new_user.id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User Login",
    description="Authenticates user credentials and returns a JWT bearer access token.",
)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
    description="Returns the profile of the currently authenticated user. Never exposes password hash.",
)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Request Password Reset Link",
    description=(
        "Generates a secure, single-use, 15-minute expiring password reset token. "
        "Returns a neutral confirmation message regardless of whether the email exists."
    ),
)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    raw_token = None
    reset_url = None

    if user:
        # Invalidate previous unused reset tokens for this student
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.is_used == False,
        ).update({"is_used": True})

        # Generate cryptographically secure random single-use token
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        reset_record = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_used=False,
        )
        db.add(reset_record)
        db.commit()

        reset_url = f"{settings.frontend_origin}/reset-password?token={raw_token}"
        send_password_reset_email(
            to_email=user.email,
            recipient_name=user.name,
            reset_url=reset_url,
        )

    # Return neutral response preventing account enumeration
    # Include reset token/url in local development when SMTP is not configured for easy testing
    is_local_dev = not settings.is_production and not settings.smtp_host
    return ForgotPasswordResponse(
        message="If an account exists for this email address, password reset instructions will be sent.",
        reset_token=raw_token if is_local_dev else None,
        reset_url=reset_url if is_local_dev else None,
    )


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    summary="Reset User Password",
    description="Resets the password for a student account using a valid, unexpired reset token.",
)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(payload.token.strip().encode("utf-8")).hexdigest()
    reset_record = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.is_used == False,
        )
        .first()
    )

    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used password reset link. Please request a new one.",
        )

    # Check expiration
    now = datetime.now(timezone.utc)
    # Ensure timezone awareness for comparison
    expires_at = reset_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now > expires_at:
        reset_record.is_used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset link has expired. Please request a new reset link.",
        )

    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated user account not found.",
        )

    # Hash new password securely with Argon2id
    user.password_hash = hash_password(payload.new_password)
    reset_record.is_used = True
    reset_record.used_at = now
    db.commit()

    return ResetPasswordResponse(
        message="Your password has been successfully reset. You can now log in with your new password.",
        success=True,
    )
