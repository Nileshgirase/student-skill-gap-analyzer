from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from app.security.password import hash_password, verify_password
from app.security.jwt_handler import create_access_token
from app.security.dependencies import get_current_user

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
    description=(
        "Authenticates user credentials and returns a JWT bearer access token. "
        "Supports both JSON payloads ({email/username, password}) and OAuth2 Form Data ({username, password})."
    ),
)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    content_type = request.headers.get("content-type", "")
    login_id = ""
    password = ""

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form = await request.form()
        login_id = str(form.get("username") or form.get("email") or "").strip()
        password = str(form.get("password") or "")
    else:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid request body. Expected JSON or Form Data.",
            )
        login_id = str(body.get("email") or body.get("username") or "").strip()
        password = str(body.get("password") or "")

    if not login_id or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Both email/username and password are required.",
        )

    # Support authentication by registered email OR student name
    user = (
        db.query(User)
        .filter(
            (User.email == login_id.lower()) | (User.name.ilike(login_id))
        )
        .first()
    )

    if not user or not verify_password(password, user.password_hash):
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
