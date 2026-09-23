from app.models.schemas import DocumentType


def detect_document_type(ocr_text: str) -> DocumentType:
    """Detect the document type using simple OCR keyword rules."""

    text = ocr_text.lower()

    if "aadhaar" in text or "unique identification authority" in text:
        return DocumentType.AADHAAR

    if "marksheet" in text or "mark sheet" in text or "senior secondary" in text or "class xii" in text or "12th" in text:
        if "class xii" in text or "12th" in text or "senior secondary" in text or "senior secondary school certificate" in text:
            return DocumentType.MARKSHEET_12TH
        if "class x" in text or "10th" in text or "secondary" in text:
            return DocumentType.MARKSHEET_10TH

    if "income certificate" in text or "annual income" in text:
        return DocumentType.INCOME_CERTIFICATE

    if "caste certificate" in text or "scheduled caste" in text:
        return DocumentType.CASTE_CERTIFICATE

    if "domicile certificate" in text or "resident of" in text:
        return DocumentType.DOMICILE_CERTIFICATE

    if "bank passbook" in text or "account number" in text:
        return DocumentType.BANK_PASSBOOK

    return DocumentType.OTHER


