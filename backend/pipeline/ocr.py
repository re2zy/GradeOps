import io
from typing import List, Tuple
from PIL import Image
import fitz  # PyMuPDF

_model = None
_processor = None
MODEL_ID = "Qwen/Qwen-VL-Chat"


def _get_model():
    global _model, _processor
    if _model is None:
        import torch
        from transformers import AutoProcessor, AutoModelForVision2Seq
        _processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)
        _model = AutoModelForVision2Seq.from_pretrained(
            MODEL_ID,
            trust_remote_code=True,
            device_map="auto",
            torch_dtype=torch.float16,
        )
    return _model, _processor


def pdf_to_images(pdf_bytes: bytes, dpi: int = 200) -> List[Image.Image]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images


def transcribe_image(image: Image.Image) -> str:
    model, processor = _get_model()
    prompt = (
        "You are an OCR assistant for handwritten exam papers. "
        "Transcribe all visible text exactly as written, preserving structure and question numbers."
    )
    inputs = processor(text=prompt, images=image, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(**inputs, max_new_tokens=1024)
    return processor.decode(output[0], skip_special_tokens=True)


def image_to_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def extract_and_crop_answers(pdf_bytes: bytes, num_questions: int) -> List[Tuple[str, bytes]]:
    """Returns (transcribed_text, page_png_bytes) for each page of the PDF."""
    images = pdf_to_images(pdf_bytes)
    results = []
    for img in images:
        text = transcribe_image(img)
        results.append((text, image_to_bytes(img)))
    return results
