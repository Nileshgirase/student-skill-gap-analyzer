"""
Pydantic validation schemas package.
"""
from app.schemas.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from app.schemas.analysis import (
    SkillInputSchema,
    SkillResponseSchema,
    AnalysisCreateRequest,
    AnalysisSummaryResponse,
    AnalysisDetailResponse,
    StudentSkillsUpdateRequest,
)
from app.schemas.job import (
    JobSnapshotResponse,
    JobSearchResponse,
)
from app.schemas.gap_analysis import (
    SkillGapItemSchema,
    AdditionalSkillSchema,
    GapAnalysisResponse,
)

__all__ = [
    "UserRegisterRequest",
    "UserLoginRequest",
    "UserResponse",
    "TokenResponse",
    "SkillInputSchema",
    "SkillResponseSchema",
    "AnalysisCreateRequest",
    "AnalysisSummaryResponse",
    "AnalysisDetailResponse",
    "StudentSkillsUpdateRequest",
    "JobSnapshotResponse",
    "JobSearchResponse",
    "SkillGapItemSchema",
    "AdditionalSkillSchema",
    "GapAnalysisResponse",
]
