from datetime import datetime
from pydantic import BaseModel, ConfigDict


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
