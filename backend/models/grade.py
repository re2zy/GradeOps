import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from database import Base


class GradeStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    overridden = "overridden"


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=True)
    extracted_answer = Column(Text, nullable=True)
    ai_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    justification = Column(Text, nullable=False)
    cropped_image_url = Column(String, nullable=True)
    plagiarism_flagged = Column(Boolean, default=False)
    plagiarism_note = Column(Text, nullable=True)

    ta_override_score = Column(Float, nullable=True)
    ta_comment = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(GradeStatus), default=GradeStatus.pending)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submission = relationship("Submission", back_populates="grades")
    reviewer = relationship("User", foreign_keys=[reviewed_by])
