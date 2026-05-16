from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from models.exam import ExamStatus
from models.submission import SubmissionStatus


class RubricCriterion(BaseModel):
    description: str
    points: float


class RubricQuestion(BaseModel):
    number: int
    text: str
    max_score: float
    criteria: List[RubricCriterion]


class RubricSchema(BaseModel):
    questions: List[RubricQuestion]


class ExamCreate(BaseModel):
    title: str
    course_code: str
    rubric: dict


class ExamOut(BaseModel):
    id: int
    title: str
    course_code: str
    instructor_id: int
    rubric: dict
    status: ExamStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class SubmissionOut(BaseModel):
    id: int
    exam_id: int
    student_name: str
    student_id: str
    pdf_url: str
    status: SubmissionStatus
    created_at: datetime

    model_config = {"from_attributes": True}
