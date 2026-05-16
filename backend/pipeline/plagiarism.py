from typing import List, Dict, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SIMILARITY_THRESHOLD = 0.85


def _compute_similarity(texts: List[str]) -> np.ndarray:
    if len(texts) < 2:
        return np.ones((len(texts), len(texts)))
    vectorizer = TfidfVectorizer(ngram_range=(1, 3), strip_accents="unicode", min_df=1)
    matrix = vectorizer.fit_transform(texts)
    return cosine_similarity(matrix)


def detect_plagiarism(
    submission_answers: List[Dict],
) -> List[Tuple[int, int, float, int]]:
    """
    submission_answers: [{"submission_id": int, "question_number": int, "answer": str}]
    Returns: [(submission_id_a, submission_id_b, similarity_score, question_number)]
    """
    flagged = []
    question_groups: Dict[int, List[Dict]] = {}

    for item in submission_answers:
        question_groups.setdefault(item["question_number"], []).append(item)

    for q_num, group in question_groups.items():
        if len(group) < 2:
            continue
        texts = [g["answer"] or "" for g in group]
        sim_matrix = _compute_similarity(texts)

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                score = float(sim_matrix[i][j])
                if score >= SIMILARITY_THRESHOLD:
                    flagged.append((group[i]["submission_id"], group[j]["submission_id"], score, q_num))

    return flagged


def check_submission_plagiarism(
    submission_id: int,
    answers: List[str],
    other_submissions: List[Dict],
) -> List[Dict]:
    """Check one submission against all others. Returns per-question flags."""
    all_items = [
        {"submission_id": submission_id, "question_number": i + 1, "answer": a}
        for i, a in enumerate(answers)
    ] + other_submissions

    flags = []
    for sid_a, sid_b, score, q_num in detect_plagiarism(all_items):
        if submission_id in (sid_a, sid_b):
            other_id = sid_b if sid_a == submission_id else sid_a
            flags.append({
                "question_number": q_num,
                "similar_submission_id": other_id,
                "similarity_score": score,
                "note": f"Answer is {score:.0%} similar to submission #{other_id}",
            })
    return flags
