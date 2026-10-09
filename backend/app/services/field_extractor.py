
import re


def extract_fields(ocr_text: str) -> dict:
    """Extract simple fields from OCR text using basic patterns."""
    fields = {}

    name_match = re.search(
        r"Name\s*:\s*([A-Za-z ]+)",
        ocr_text,
        re.IGNORECASE
    )
    if name_match:
        fields["name"] = name_match.group(1).strip()

    dob_match = re.search(
        r"(?:Date of Birth|DOB)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
        ocr_text,
        re.IGNORECASE
    )
    if dob_match:
        fields["date_of_birth"] = dob_match.group(1)

    income_match = re.search(
        r"(?:annual\s+family\s+income|family\s+income|annual\s+income|income)"
        r"\s*(?:per\s+annum|per\s+year)?\s*"
        r"[:\-]?\s*(?:Rs\.?|INR|₹)?\s*"
        r"([0-9][0-9,]*(?:\.[0-9]+)?)",
        ocr_text,
        re.IGNORECASE
    )
    if income_match:
        fields["income"] = income_match.group(1).replace(",", "")

    marks_match = re.search(
        r"(?:Marks|Percentage)\s*:?\s*([0-9]+(?:\.[0-9]+)?)\s*%?",
        ocr_text,
        re.IGNORECASE
    )
    if marks_match:
        fields["percentage"] = marks_match.group(1)

    return fields
