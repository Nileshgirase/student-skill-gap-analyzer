from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StudentProfile(Base):
    """
    SQLAlchemy model representing extended academic and personal profile details for a student.
    """
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    mobile_number = Column(String(30), nullable=True)
    college_name = Column(String(200), nullable=True)
    degree = Column(String(100), nullable=True)
    specialization = Column(String(100), nullable=True)
    graduation_year = Column(Integer, nullable=True)
    weekly_study_hours = Column(Integer, default=10, nullable=False)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    current_skills_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    user = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<StudentProfile(id={self.id}, user_id={self.user_id}, college='{self.college_name}')>"
