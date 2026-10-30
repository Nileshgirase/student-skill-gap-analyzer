import re
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class StudentProfileResponse(BaseModel):
    """Safe public representation of the student profile."""
    user_id: int
    name: str
    email: str
    mobile_number: str | None = None
    college_name: str | None = None
    degree: str | None = None
    specialization: str | None = None
    graduation_year: int | None = None
    weekly_study_hours: int = 10
    avatar_url: str | None = None
    bio: str | None = None
    current_skills: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentProfileUpdateRequest(BaseModel):
    """Payload for updating student profile details."""
    name: str = Field(..., min_length=2, max_length=100, description="Full student name")
    mobile_number: str | None = Field(default=None, max_length=25, description="Mobile contact number")
    college_name: str | None = Field(default=None, max_length=200, description="College or university name")
    degree: str | None = Field(default=None, max_length=100, description="Degree or program (e.g. B.Tech, B.S.)")
    specialization: str | None = Field(default=None, max_length=100, description="Major / Specialization (e.g. Computer Science)")
    graduation_year: int | None = Field(default=None, ge=1970, le=2050, description="Year of graduation")
    weekly_study_hours: int = Field(default=10, ge=1, le=100, description="Weekly hours dedicated to skill improvement")
    avatar_url: str | None = Field(default=None, max_length=500, description="Profile avatar URL or preset identifier")
    bio: str | None = Field(default=None, max_length=500, description="Brief student bio or career objectives")
    current_skills: list[str] = Field(default_factory=list, description="Self-reported primary skills")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        clean = value.strip()
        if len(clean) < 2:
            raise ValueError("Full name must be at least 2 characters long.")
        return clean

    @field_validator("mobile_number")
    @classmethod
    def validate_mobile(cls, value: str | None) -> str | None:
        if not value:
            return None
        clean = value.strip()
        if not clean:
            return None
        # Allow formats like +91 9876543210, +1 (555) 000-0000, 9876543210
        if not re.match(r"^\+?[0-9\s\-\(\)\.]{7,25}$", clean):
            raise ValueError("Invalid mobile number format. Please provide a valid phone number.")
        return clean

    @field_validator("college_name", "degree", "specialization", "avatar_url", "bio")
    @classmethod
    def clean_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        clean = value.strip()
        return clean if clean else None
