from typing import Optional
from pydantic import BaseModel
from models.grade import GradeStatus


class GradeOut(BaseModel):
    id: int
    submission_id: int
    question_number: int
    question_text: Optional[str] = None
    extracted_answer: Optional[str] = None
    ai_score: float
    max_score: float
    justification: str
    cropped_image_url: Optional[str] = None
    plagiarism_flagged: bool
    plagiarism_note: Optional[str] = None
    ta_override_score: Optional[float] = None
    ta_comment: Optional[str] = None
    status: GradeStatus

    model_config = {"from_attributes": True}


class GradeReview(BaseModel):
    action: str  # "approve" or "override"
    ta_override_score: Optional[float] = None
    ta_comment: Optional[str] = None
