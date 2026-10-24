from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StudentSkill(Base):
    """
    SQLAlchemy model representing a skill reported by a student for a specific analysis.
    """
    __tablename__ = "student_skills"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(
        Integer,
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name = Column(String(100), nullable=False)
    canonical_skill = Column(String(100), nullable=False, index=True)
    proficiency_level = Column(String(20), default="beginner", nullable=False)
    self_reported = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    analysis = relationship("Analysis", back_populates="student_skills")

    def __repr__(self) -> str:
        return (
            f"<StudentSkill(id={self.id}, analysis_id={self.analysis_id}, "
            f"name='{self.skill_name}', canonical='{self.canonical_skill}', "
            f"proficiency='{self.proficiency_level}')>"
        )
