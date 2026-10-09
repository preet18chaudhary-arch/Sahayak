
from pathlib import Path
import os

import fitz
import pytesseract
from PIL import Image


# Configure Tesseract for the operating system.
if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
else:
    import tesseract_bin

    pytesseract.pytesseract.tesseract_cmd = (
        tesseract_bin.TESSERACT_PATH
    )
    os.environ.setdefault(
        "TESSDATA_PREFIX",
        tesseract_bin.TESSDATA_PREFIX
    )


def extract_text_from_image(file_path: str) -> str:
    """Extract text from PDF and image files using Tesseract OCR."""

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extracted_pages = []

    if file_path.suffix.lower() == ".pdf":
        # Convert each PDF page into an image for OCR.
        with fitz.open(file_path) as pdf:
            for page in pdf:
                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False
                )

                image = Image.frombytes(
                    "RGB",
                    (pixmap.width, pixmap.height),
                    pixmap.samples
                )

                extracted_pages.append(
                    pytesseract.image_to_string(image)
                )
    else:
        # Handle image files such as PNG and JPG.
        with Image.open(file_path) as image:
            extracted_pages.append(
                pytesseract.image_to_string(image.convert("RGB"))
            )

    return "\n".join(extracted_pages).strip()
