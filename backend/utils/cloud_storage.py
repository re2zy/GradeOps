import os
import uuid

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def upload_file(file_bytes: bytes, blob_name: str, content_type: str) -> str:
    safe_name = blob_name.replace("/", "_")
    path = os.path.join(UPLOAD_DIR, safe_name)
    with open(path, "wb") as f:
        f.write(file_bytes)
    return f"http://localhost:8000/uploads/{safe_name}"

def upload_exam_pdf(file_bytes: bytes, exam_id: int, submission_id: int) -> str:
    blob_name = f"exam_{exam_id}_submission_{submission_id}_{uuid.uuid4().hex}.pdf"
    return upload_file(file_bytes, blob_name, "application/pdf")

def upload_cropped_image(file_bytes: bytes, exam_id: int, submission_id: int, question_num: int) -> str:
    blob_name = f"exam_{exam_id}_sub_{submission_id}_q{question_num}_{uuid.uuid4().hex}.png"
    return upload_file(file_bytes, blob_name, "image/png")

def download_file(blob_name: str) -> bytes:
    safe_name = blob_name.replace("/", "_")
    path = os.path.join(UPLOAD_DIR, safe_name)
    with open(path, "rb") as f:
        return f.read()

def download_cropped_image(url: str) -> bytes:
    blob_name = url.replace("local://uploads/", "")
    return download_file(blob_name)