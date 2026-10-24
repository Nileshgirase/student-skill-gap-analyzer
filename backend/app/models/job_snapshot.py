from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JobSnapshot(Base):
    """
    SQLAlchemy model representing a verified job posting snapshot retrieved from a source.
    Preserves exact evidence, source URL, fetch date, and freshness status.
    """
    __tablename__ = "job_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_name = Column(String(100), nullable=False)
    source_url = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)
    employer_name = Column(String(100), nullable=False)
    job_title = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    employment_type = Column(String(100), nullable=True)
    description_text = Column(Text, nullable=False)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    content_hash = Column(String(64), nullable=True, index=True)
    is_stale = Column(Boolean, default=False, nullable=False)
    verification_status = Column(String(50), default="verified", nullable=False)
    verification_notes = Column(Text, nullable=True)

    # Relationships
    analysis = relationship("Analysis", back_populates="job_snapshots")

    def __repr__(self) -> str:
        return (
            f"<JobSnapshot(id={self.id}, title='{self.job_title}', "
            f"employer='{self.employer_name}', source='{self.source_name}')>"
        )
