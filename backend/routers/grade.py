from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.grade import Grade
from models.submission import Submission
from models.user import User
from schemas.grade import GradeOut
from utils.jwt import get_current_user

router = APIRouter(prefix="/grades", tags=["grades"])


@router.get("/submission/{submission_id}", response_model=List[GradeOut])
def get_grades_for_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(Submission).filter(Submission.id == submission_id).first():
        raise HTTPException(status_code=404, detail="Submission not found")
    return (
        db.query(Grade)
        .filter(Grade.submission_id == submission_id)
        .order_by(Grade.question_number)
        .all()
    )


@router.get("/exam/{exam_id}/summary")
def get_exam_grade_summary(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    submissions = db.query(Submission).filter(Submission.exam_id == exam_id).all()
    summary = []
    for sub in submissions:
        grades = db.query(Grade).filter(Grade.submission_id == sub.id).all()
        ai_total = sum(g.ai_score for g in grades)
        final_total = sum(
            g.ta_override_score if g.ta_override_score is not None else g.ai_score
            for g in grades
        )
        max_total = sum(g.max_score for g in grades)
        summary.append({
            "submission_id": sub.id,
            "student_name": sub.student_name,
            "student_id": sub.student_id,
            "status": sub.status,
            "ai_total": ai_total,
            "final_total": final_total,
            "max_total": max_total,
            "questions_pending": sum(1 for g in grades if g.status == "pending"),
        })
    return summary
