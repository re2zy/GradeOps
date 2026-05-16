import uuid
from google.cloud import storage
from config import get_settings

settings = get_settings()
_client = None


def _get_client() -> storage.Client:
    global _client
    if _client is None:
        _client = storage.Client()
    return _client


def upload_file(file_bytes: bytes, blob_name: str, content_type: str = "application/octet-stream") -> str:
    client = _get_client()
    bucket = client.bucket(settings.gcs_bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(file_bytes, content_type=content_type)
    blob.make_public()
    return blob.public_url


def upload_exam_pdf(file_bytes: bytes, exam_id: int, student_id: str) -> str:
    blob_name = f"exams/{exam_id}/submissions/{student_id}/{uuid.uuid4()}.pdf"
    return upload_file(file_bytes, blob_name, "application/pdf")


def upload_cropped_image(image_bytes: bytes, submission_id: int, question_num: int) -> str:
    blob_name = f"crops/submission_{submission_id}/q{question_num}_{uuid.uuid4()}.png"
    return upload_file(image_bytes, blob_name, "image/png")
