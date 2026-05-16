"""Seed the database with demo users and an exam. Run from the repo root:
   PYTHONPATH=backend python scripts/seed_db.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from database import engine, SessionLocal, Base
from models.user import User, UserRole
from models.exam import Exam, ExamStatus
from utils.jwt import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).filter(User.email == "instructor@gradeops.com").first():
        print("Already seeded — skipping.")
        db.close()
        return

    instructor = User(
        email="instructor@gradeops.com",
        hashed_password=hash_password("password123"),
        full_name="Demo Instructor",
        role=UserRole.instructor,
    )
    ta = User(
        email="ta@gradeops.com",
        hashed_password=hash_password("password123"),
        full_name="Demo TA",
        role=UserRole.ta,
    )
    db.add_all([instructor, ta])
    db.commit()
    db.refresh(instructor)

    exam = Exam(
        title="Data Structures Midterm",
        course_code="CS201",
        instructor_id=instructor.id,
        status=ExamStatus.active,
        rubric={
            "questions": [
                {
                    "number": 1,
                    "text": "Explain the difference between a stack and a queue.",
                    "max_score": 10,
                    "criteria": [
                        {"description": "Correct definition of stack (LIFO)", "points": 4},
                        {"description": "Correct definition of queue (FIFO)", "points": 4},
                        {"description": "Gives a real-world example for each", "points": 2},
                    ],
                },
                {
                    "number": 2,
                    "text": "Write pseudocode for binary search.",
                    "max_score": 15,
                    "criteria": [
                        {"description": "Correct base case / termination condition", "points": 5},
                        {"description": "Correct mid-point calculation", "points": 5},
                        {"description": "Correct recursive or iterative structure", "points": 5},
                    ],
                },
            ]
        },
    )
    db.add(exam)
    db.commit()

    print("Seeded:")
    print("  instructor@gradeops.com / password123  (role: instructor)")
    print("  ta@gradeops.com         / password123  (role: ta)")
    print(f"  Exam: '{exam.title}' (ID: {exam.id})")
    db.close()


if __name__ == "__main__":
    seed()
