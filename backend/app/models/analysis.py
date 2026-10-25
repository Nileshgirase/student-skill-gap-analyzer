from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Analysis(Base):
    """
    SQLAlchemy model representing a skill gap analysis request initiated by a student.
    """
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company_name = Column(String(100), nullable=False)
    target_role = Column(String(100), nullable=False)
    weekly_hours = Column(Integer, nullable=False)
    status = Column(String(50), default="pending", nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="analyses")
    student_skills = relationship(
        "StudentSkill",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="StudentSkill.id",
    )
    job_snapshots = relationship(
        "JobSnapshot",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="JobSnapshot.id",
    )
    roadmap_items = relationship(
        "RoadmapItem",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="RoadmapItem.week_number",
    )

    def __repr__(self) -> str:
        return (
            f"<Analysis(id={self.id}, user_id={self.user_id}, "
            f"company='{self.company_name}', role='{self.target_role}', status='{self.status}')>"
        )
