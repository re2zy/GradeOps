import json
import re
import os
from typing import Dict, Any, List
from groq import Groq
from pipeline.rubric_parser import build_grading_prompt, parse_rubric

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client

def grade_answer(question: Dict[str, Any], student_answer: str) -> Dict[str, Any]:
    client = _get_client()
    prompt = build_grading_prompt(question, student_answer)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    content = response.choices[0].message.content
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