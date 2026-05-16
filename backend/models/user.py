import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base


class UserRole(str, enum.Enum):
    instructor = "instructor"
    ta = "ta"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ta)
    created_at = Column(DateTime, default=datetime.utcnow)

    exams = relationship("Exam", back_populates="instructor", foreign_keys="Exam.instructor_id")
