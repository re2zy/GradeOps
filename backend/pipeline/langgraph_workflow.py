import asyncio
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from models.submission import Submission, SubmissionStatus
from models.grade import Grade, GradeStatus
from utils.cloud_storage import upload_cropped_image
from pipeline.ocr import extract_and_crop_answers
from pipeline.rubric_parser import parse_rubric
from pipeline.grader_agent import grade_submission
from pipeline.plagiarism import check_submission_plagiarism


class GradingState(TypedDict):
    submission_id: int
    exam_id: int
    rubric: dict
    pdf_bytes: bytes
    extracted_answers: List[str]
    cropped_image_urls: List[str]
    grades: List[dict]
    plagiarism_flags: List[dict]
    error: Optional[str]


def node_extract(state: GradingState) -> GradingState:
    try:
        rubric = parse_rubric(state["rubric"])
        results = extract_and_crop_answers(state["pdf_bytes"], len(rubric.questions))

        answers = [text for text, _ in results]
        crop_urls = []
        for i, (_, img_bytes) in enumerate(results):
            url = upload_cropped_image(img_bytes, state["submission_id"], i + 1)
            crop_urls.append(url)

        return {**state, "extracted_answers": answers, "cropped_image_urls": crop_urls}
    except Exception as exc:
        return {**state, "error": str(exc)}


def node_grade(state: GradingState) -> GradingState:
    if state.get("error"):
        return state
    try:
        grades = grade_submission(state["rubric"], state["extracted_answers"])
        return {**state, "grades": grades}
    except Exception as exc:
        return {**state, "error": str(exc)}


def node_plagiarism(state: GradingState) -> GradingState:
    if state.get("error"):
        return state
    try:
        flags = check_submission_plagiarism(
            state["submission_id"],
            state["extracted_answers"],
            [],  # TODO: pass other submissions' answers from DB
        )
        return {**state, "plagiarism_flags": flags}
    except Exception as exc:
        return {**state, "error": str(exc)}


def _route(state: GradingState) -> str:
    return "error" if state.get("error") else "continue"


def build_workflow():
    wf = StateGraph(GradingState)
    wf.add_node("extract", node_extract)
    wf.add_node("grade", node_grade)
    wf.add_node("plagiarism", node_plagiarism)

    wf.set_entry_point("extract")
    wf.add_conditional_edges("extract", _route, {"continue": "grade", "error": END})
    wf.add_conditional_edges("grade", _route, {"continue": "plagiarism", "error": END})
    wf.add_edge("plagiarism", END)

    return wf.compile()


_workflow = None


def get_workflow():
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow


def _persist_results(state: GradingState, db: Session) -> None:
    submission = db.query(Submission).filter(Submission.id == state["submission_id"]).first()
    if not submission:
        return

    plagiarism_map = {f["question_number"]: f for f in state.get("plagiarism_flags", [])}

    for i, gd in enumerate(state.get("grades", [])):
        q_num = gd["question_number"]
        plag = plagiarism_map.get(q_num, {})
        grade = Grade(
            submission_id=state["submission_id"],
            question_number=q_num,
            question_text=gd.get("question_text"),
            extracted_answer=state["extracted_answers"][i] if i < len(state["extracted_answers"]) else None,
            ai_score=gd["score"],
            max_score=gd["max_score"],
            justification=gd["justification"],
            cropped_image_url=state["cropped_image_urls"][i] if i < len(state["cropped_image_urls"]) else None,
            plagiarism_flagged=bool(plag),
            plagiarism_note=plag.get("note"),
            status=GradeStatus.pending,
        )
        db.add(grade)

    submission.status = SubmissionStatus.graded
    db.commit()


async def run_grading_pipeline(
    submission_id: int,
    exam_id: int,
    rubric: dict,
    pdf_bytes: bytes,
    db: Session,
) -> None:
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    submission.status = SubmissionStatus.processing
    db.commit()

    initial: GradingState = {
        "submission_id": submission_id,
        "exam_id": exam_id,
        "rubric": rubric,
        "pdf_bytes": pdf_bytes,
        "extracted_answers": [],
        "cropped_image_urls": [],
        "grades": [],
        "plagiarism_flags": [],
        "error": None,
    }

    final = await asyncio.to_thread(get_workflow().invoke, initial)

    if final.get("error"):
        submission.status = SubmissionStatus.error
        db.commit()
    else:
        _persist_results(final, db)
