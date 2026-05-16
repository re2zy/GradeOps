import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from database import Base


class ExamStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    grading = "grading"
    completed = "completed"


class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    course_code = Column(String, nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rubric = Column(JSON, nullable=False)
    status = Column(Enum(ExamStatus), default=ExamStatus.draft)
    created_at = Column(DateTime, default=datetime.utcnow)

    instructor = relationship("User", back_populates="exams", foreign_keys=[instructor_id])
    submissions = relationship("Submission", back_populates="exam")
