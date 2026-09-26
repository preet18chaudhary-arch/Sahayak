from pathlib import Path

import pytesseract
from PIL import Image


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_image(file_path: str) -> str:
    """Extract text from an image using Tesseract OCR."""

    image_path = Path(file_path)

    if not image_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    text = pytesseract.image_to_string(Image.open(image_path))

    return text.strip()
