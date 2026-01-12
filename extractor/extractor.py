from pdfminer.high_level import extract_text
from PIL import Image
import pytesseract
import os

def extract_resume_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text(file_path)

    elif ext in [".png", ".jpg", ".jpeg"]:
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)

    else:
        raise ValueError("Unsupported file format")
