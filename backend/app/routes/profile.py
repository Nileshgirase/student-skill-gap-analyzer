import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.profile import StudentProfileResponse, StudentProfileUpdateRequest
from app.security.dependencies import get_current_user

router = APIRouter(prefix="/api/profile", tags=["Student Profile"])


def get_or_create_profile(user: User, db: Session) -> StudentProfile:
    """Retrieves existing profile or initializes a default profile for the user."""
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        profile = StudentProfile(
            user_id=user.id,
            weekly_study_hours=10,
            current_skills_json="[]",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get(
    "",
    response_model=StudentProfileResponse,
    summary="Get Student Profile",
    description="Returns the personal and academic profile details of the authenticated student.",
)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_profile(current_user, db)

    skills_list = []
    if profile.current_skills_json:
        try:
            skills_list = json.loads(profile.current_skills_json)
        except Exception:
            skills_list = []

    return StudentProfileResponse(
        user_id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        mobile_number=profile.mobile_number,
        college_name=profile.college_name,
        degree=profile.degree,
        specialization=profile.specialization,
        graduation_year=profile.graduation_year,
        weekly_study_hours=profile.weekly_study_hours,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        current_skills=skills_list,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.put(
    "",
    response_model=StudentProfileResponse,
    summary="Update Student Profile",
    description="Updates the authenticated student's profile information while keeping authentication credentials secure.",
)
def update_profile(
    payload: StudentProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_or_create_profile(current_user, db)

    # 1. Update User name
    current_user.name = payload.name

    # 2. Update StudentProfile fields
    profile.mobile_number = payload.mobile_number
    profile.college_name = payload.college_name
    profile.degree = payload.degree
    profile.specialization = payload.specialization
    profile.graduation_year = payload.graduation_year
    profile.weekly_study_hours = payload.weekly_study_hours
    profile.avatar_url = payload.avatar_url
    profile.bio = payload.bio
    profile.current_skills_json = json.dumps(payload.current_skills)

    db.commit()
    db.refresh(current_user)
    db.refresh(profile)

    return StudentProfileResponse(
        user_id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        mobile_number=profile.mobile_number,
        college_name=profile.college_name,
        degree=profile.degree,
        specialization=profile.specialization,
        graduation_year=profile.graduation_year,
        weekly_study_hours=profile.weekly_study_hours,
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        current_skills=payload.current_skills,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
