from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RoadmapItem(Base):
    """
    SQLAlchemy model representing a scheduled, personalized learning task
    scheduled within the student's weekly study budget.
    """
    __tablename__ = "roadmap_items"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    week_number = Column(Integer, nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    canonical_skill = Column(String(100), nullable=False, index=True)
    learning_goal = Column(Text, nullable=False)
    resource_title = Column(String(255), nullable=False)
    resource_url = Column(String(500), nullable=False)
    resource_provider = Column(String(100), nullable=False)
    estimated_hours = Column(Float, nullable=False)
    status = Column(
        String(20),
        default="not_started",
        nullable=False,
    )  # 'not_started', 'in_progress', 'completed'
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    # Relationships
    analysis = relationship("Analysis", back_populates="roadmap_items")

    def __repr__(self) -> str:
        return (
            f"<RoadmapItem(id={self.id}, week={self.week_number}, "
            f"skill='{self.skill_name}', status='{self.status}')>"
        )
