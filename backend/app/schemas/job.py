from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class JobSnapshotResponse(BaseModel):
    """Output representation of a verified job snapshot."""
    id: int
    analysis_id: int
    source_name: str
    source_url: str
    source_type: str
    employer_name: str
    job_title: str
    location: str | None = None
    employment_type: str | None = None
    description_text: str
    fetched_at: datetime
    posted_at: datetime | None = None
    is_stale: bool = False
    verification_status: str
    verification_notes: str | None = None

    model_config = ConfigDict(from_attributes=True)


class JobSearchResponse(BaseModel):
    """Response returned upon running the job search for an analysis."""
    status: str
    company: str
    target_role: str
    message: str
    jobs: list[JobSnapshotResponse] = []
    has_cached_snapshots: bool = False
    cached_snapshot_count: int = 0
    cached_snapshot_title: str | None = None
    cached_snapshot_date: datetime | None = None
    cached_snapshot_employer: str | None = None
    has_industry_benchmark: bool = False
    industry_benchmark_role: str | None = None


class UserProvidedJobRequest(BaseModel):
    """Payload for directly pasting or providing a job description."""
    description_text: str = Field(
        ...,
        min_length=20,
        max_length=50000,
        description="Full text or excerpt of the job description from career page or job board",
    )
    job_title: str | None = Field(default=None, max_length=200, description="Optional job title")
    source_url: str | None = Field(default=None, max_length=500, description="Optional URL to job posting")
