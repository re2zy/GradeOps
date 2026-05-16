import json
import re
from typing import Dict, Any, List
from anthropic import Anthropic
from config import get_settings
from pipeline.rubric_parser import build_grading_prompt, parse_rubric

settings = get_settings()
_client = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def grade_answer(question: Dict[str, Any], student_answer: str) -> Dict[str, Any]:
    client = _get_client()
    prompt = build_grading_prompt(question, student_answer)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.content[0].text
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    if not json_match:
        raise ValueError(f"Grader returned non-JSON response: {content[:200]}")

    result = json.loads(json_match.group())
    return {
        "score": min(float(result["score"]), question["max_score"]),
        "justification": result["justification"],
        "criteria_met": result.get("criteria_met", []),
        "criteria_missed": result.get("criteria_missed", []),
    }


def grade_submission(rubric: dict, answers: List[str]) -> List[Dict[str, Any]]:
    schema = parse_rubric(rubric)
    grades = []
    for question in schema.questions:
        answer = answers[question.number - 1] if question.number <= len(answers) else ""
        result = grade_answer(question.model_dump(), answer)
        grades.append({
            "question_number": question.number,
            "question_text": question.text,
            "max_score": question.max_score,
            **result,
        })
    return grades
