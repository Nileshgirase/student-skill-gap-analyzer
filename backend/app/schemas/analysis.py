from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.schemas.job import JobSnapshotResponse

ProficiencyType = Literal["beginner", "intermediate", "advanced", "unknown"]


class SkillInputSchema(BaseModel):
    """Input payload for a single skill reported by the student."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the skill")
    proficiency: ProficiencyType = Field(
        default="beginner",
        description="Self-reported proficiency: beginner, intermediate, advanced, or unknown",
    )

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("Skill name cannot be empty or only whitespace.")
        return clean


class SkillResponseSchema(BaseModel):
    """Output representation of a student skill."""
    id: int
    analysis_id: int
    skill_name: str
    canonical_skill: str
    proficiency_level: str
    self_reported: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisCreateRequest(BaseModel):
    """Input payload for initiating a skill gap analysis."""
    company_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Target company name as free text (e.g. Google, TCS, Stripe)",
    )
    target_role: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Target job role as free text (e.g. Data Analyst, Software Engineer)",
    )
    weekly_hours: int = Field(
        ...,
        ge=1,
        le=100,
        description="Available weekly study hours (positive integer between 1 and 100)",
    )
    student_skills: list[SkillInputSchema] = Field(
        default_factory=list,
        description="List of current skills and self-reported proficiencies",
    )

    @field_validator("company_name", "target_role")
    @classmethod
    def clean_text_fields(cls, value: str) -> str:
        clean = value.strip()
        if not clean:
            raise ValueError("Field cannot be blank or only whitespace.")
        return clean


class AnalysisSummaryResponse(BaseModel):
    """Compact summary of an analysis for dashboard listings."""
    id: int
    company_name: str
    target_role: str
    weekly_hours: int
    status: str
    skill_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisDetailResponse(BaseModel):
    """Detailed analysis representation including associated student skills."""
    id: int
    user_id: int
    company_name: str
    target_role: str
    weekly_hours: int
    status: str
    created_at: datetime
    updated_at: datetime
    student_skills: list[SkillResponseSchema] = []
    job_snapshots: list[JobSnapshotResponse] = []
    has_cached_snapshots: bool = False
    cached_snapshot_title: str | None = None
    cached_snapshot_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StudentSkillsUpdateRequest(BaseModel):
    """Payload for updating or replacing student skills for an existing analysis."""
    student_skills: list[SkillInputSchema] = Field(
        default_factory=list,
        description="Updated list of student skills and proficiencies",
    )
