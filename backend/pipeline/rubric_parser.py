from typing import Dict, Any
from schemas.exam import RubricSchema, RubricQuestion


def parse_rubric(rubric_data: dict) -> RubricSchema:
    return RubricSchema(**rubric_data)


def get_question(rubric: dict, question_number: int) -> RubricQuestion:
    schema = parse_rubric(rubric)
    for q in schema.questions:
        if q.number == question_number:
            return q
    raise ValueError(f"Question {question_number} not found in rubric")


def build_grading_prompt(question: Dict[str, Any], student_answer: str) -> str:
    criteria_text = "\n".join(
        f"  - {c['description']}: {c['points']} points"
        for c in question["criteria"]
    )
    return f"""You are grading a handwritten exam answer. Be strict but fair.

Question {question['number']}: {question['text']}
Maximum Score: {question['max_score']} points

Grading Criteria:
{criteria_text}

Student's Answer (transcribed from handwriting):
{student_answer or "(no answer provided)"}

Respond ONLY with valid JSON:
{{
  "score": <number between 0 and {question['max_score']}>,
  "justification": "<detailed explanation referencing specific criteria>",
  "criteria_met": ["<criteria descriptions met>"],
  "criteria_missed": ["<criteria descriptions not met>"]
}}"""
