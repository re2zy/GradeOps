import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base


class SubmissionStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    graded = "graded"
    error = "error"


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    student_name = Column(String, nullable=False)
    student_id = Column(String, nullable=False)
    pdf_url = Column(String, nullable=False)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    exam = relationship("Exam", back_populates="submissions")
    grades = relationship("Grade", back_populates="submission")
