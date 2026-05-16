import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db
from models.exam import Exam
from models.submission import Submission, SubmissionStatus
from models.user import User
from schemas.exam import ExamCreate, ExamOut, SubmissionOut
from utils.jwt import require_instructor, get_current_user
from utils.cloud_storage import upload_exam_pdf
from pipeline.langgraph_workflow import run_grading_pipeline

router = APIRouter(prefix="/exams", tags=["exams"])


@router.post("/", response_model=ExamOut, status_code=201)
def create_exam(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor),
):
    exam = Exam(
        title=exam_data.title,
        course_code=exam_data.course_code,
        instructor_id=current_user.id,
        rubric=exam_data.rubric,
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@router.get("/", response_model=List[ExamOut])
def list_exams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Exam).all()


@router.get("/{exam_id}", response_model=ExamOut)
def get_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.post("/{exam_id}/submissions", response_model=List[SubmissionOut], status_code=201)
async def upload_submissions(
    exam_id: int,
    background_tasks: BackgroundTasks,
    student_names: str = Form(...),
    student_ids: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_instructor),
):
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    names = json.loads(student_names)
    ids = json.loads(student_ids)
    if len(files) != len(names) or len(files) != len(ids):
        raise HTTPException(status_code=400, detail="Mismatch between files and student info counts")

    submissions = []
    for file, name, sid in zip(files, names, ids):
        pdf_bytes = await file.read()
        pdf_url = upload_exam_pdf(pdf_bytes, exam_id, sid)

        submission = Submission(
            exam_id=exam_id,
            student_name=name,
            student_id=sid,
            pdf_url=pdf_url,
            status=SubmissionStatus.pending,
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        submissions.append(submission)

        background_tasks.add_task(
            run_grading_pipeline,
            submission.id,
            exam_id,
            exam.rubric,
            pdf_bytes,
            db,
        )

    return submissions


@router.get("/{exam_id}/submissions", response_model=List[SubmissionOut])
def get_submissions(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Submission).filter(Submission.exam_id == exam_id).all()
