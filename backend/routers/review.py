from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.grade import Grade, GradeStatus
from models.submission import Submission
from models.user import User
from schemas.grade import GradeOut, GradeReview
from utils.jwt import require_ta

router = APIRouter(prefix="/review", tags=["review"])


@router.get("/pending", response_model=List[GradeOut])
def get_pending_grades(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ta),
):
    return (
        db.query(Grade)
        .join(Submission)
        .filter(Submission.exam_id == exam_id, Grade.status == GradeStatus.pending)
        .order_by(Grade.submission_id, Grade.question_number)
        .all()
    )


@router.post("/{grade_id}", response_model=GradeOut)
def review_grade(
    grade_id: int,
    review: GradeReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ta),
):
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")

    if review.action == "approve":
        grade.status = GradeStatus.approved
        grade.reviewed_by = current_user.id
    elif review.action == "override":
        if review.ta_override_score is None:
            raise HTTPException(status_code=400, detail="ta_override_score is required for override")
        if not (0 <= review.ta_override_score <= grade.max_score):
            raise HTTPException(status_code=400, detail=f"Score must be between 0 and {grade.max_score}")
        grade.status = GradeStatus.overridden
        grade.ta_override_score = review.ta_override_score
        grade.ta_comment = review.ta_comment
        grade.reviewed_by = current_user.id
    else:
        raise HTTPException(status_code=400, detail="action must be 'approve' or 'override'")

    db.commit()
    db.refresh(grade)
    return grade


@router.get("/stats/{exam_id}")
def get_review_stats(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ta),
):
    grades = (
        db.query(Grade)
        .join(Submission)
        .filter(Submission.exam_id == exam_id)
        .all()
    )
    total = len(grades)
    approved = sum(1 for g in grades if g.status == GradeStatus.approved)
    overridden = sum(1 for g in grades if g.status == GradeStatus.overridden)
    return {
        "total": total,
        "pending": sum(1 for g in grades if g.status == GradeStatus.pending),
        "approved": approved,
        "overridden": overridden,
        "plagiarism_flagged": sum(1 for g in grades if g.plagiarism_flagged),
        "progress_pct": round((approved + overridden) / total * 100) if total else 0,
    }
