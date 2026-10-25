from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RequiredSkill(Base):
    """
    SQLAlchemy model representing an evidence-backed skill requirement
    extracted directly from a verified job snapshot.
    """
    __tablename__ = "required_skills"

    id = Column(Integer, primary_key=True, index=True)
    job_snapshot_id = Column(
        Integer,
        ForeignKey("job_snapshots.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name = Column(String(100), nullable=False)
    canonical_skill = Column(String(100), nullable=False, index=True)
    requirement_type = Column(
        String(20),
        default="required",
        nullable=False,
    )  # 'required', 'preferred', 'mentioned', or 'uncertain'
    evidence_text = Column(Text, nullable=False)
    evidence_start = Column(Integer, nullable=True)
    evidence_end = Column(Integer, nullable=True)
    extraction_method = Column(String(50), default="dictionary_phrase_match", nullable=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    job_snapshot = relationship("JobSnapshot", back_populates="required_skills")

    def __repr__(self) -> str:
        return (
            f"<RequiredSkill(id={self.id}, name='{self.skill_name}', "
            f"type='{self.requirement_type}', snapshot_id={self.job_snapshot_id})>"
        )
