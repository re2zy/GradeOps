import io
import os
import base64
from typing import List, Tuple
from PIL import Image
import fitz
from groq import Groq

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    return _client

def pdf_to_images(pdf_bytes: bytes, dpi: int = 200) -> List[Image.Image]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for page in doc:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def split_page_into_sections(image: Image.Image, num_sections: int) -> List[Image.Image]:
    width, height = image.size
    top_offset = int(height * 0.15)
    usable_height = height - top_offset
    section_height = usable_height // num_sections
    sections = []
    for i in range(num_sections):
        top = top_offset + (i * section_height)
        bottom = top_offset + ((i + 1) * section_height) if i < num_sections - 1 else height
        section = image.crop((0, top, width, bottom))
        sections.append(section)
    return sections

def transcribe_image(image: Image.Image) -> str:
    client = _get_client()
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    image_bytes = buf.getvalue()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Transcribe only the student's answer text visible in this image. Output the transcribed text only, no explanations, no steps, no commentary."
                    }
                ]
            }
        ],
        max_tokens=2048,
    )
    return response.choices[0].message.content

def image_to_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()

def extract_and_crop_answers(pdf_bytes: bytes, num_questions: int) -> List[Tuple[str, bytes]]:
    images = pdf_to_images(pdf_bytes)
    full_page = images[0] if images else None

    if full_page is None:
        return []

    sections = split_page_into_sections(full_page, num_questions)

    results = []
    for section in sections:
        text = transcribe_image(section)
        results.append((text, image_to_bytes(section)))

    return results