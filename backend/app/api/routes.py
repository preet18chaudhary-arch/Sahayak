from typing import List
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from app.models.schemas import (
    CreateSessionRequest,
    ScholarshipRuleConfig,
    VerificationSession,
    ReadinessStatus,
)
from app.services.rule_registry import (
    get_available_scholarships,
    get_scholarship_rule_by_id,
)
from app.services.session_store import session_store

router = APIRouter(prefix="/api", tags=["Sahayak Verification"])


@router.get(
    "/scholarships",
    response_model=List[ScholarshipRuleConfig],
    summary="List configurable scholarship schemes",
    description="Returns pre-registered scholarship rules with their required documents, income ceilings, and matching thresholds.",
)
async def list_scholarships():
    """Retrieve all available scholarship rule profiles."""
    return get_available_scholarships()


@router.post(
    "/sessions/create",
    response_model=VerificationSession,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new verification session",
    description="Initializes a new verification session with either a preset scholarship scheme or a fully customized rule profile.",
)
async def create_session(request: CreateSessionRequest):
    """
    Create a verification session.
    If `custom_rules` are provided, they take priority.
    Otherwise, the rule profile corresponding to `scholarship_id` is applied.
    """
    rule_config: ScholarshipRuleConfig

    if request.custom_rules:
        rule_config = request.custom_rules
    else:
        preset_id = request.scholarship_id or "merit-cum-means"
        preset = get_scholarship_rule_by_id(preset_id)

        if not preset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scholarship scheme '{preset_id}' was not found. Use GET /api/scholarships to inspect available presets.",
            )

        rule_config = preset

    session = session_store.create_session(
        student_name=request.student_name,
        rule_config=rule_config,
    )

    return session


@router.get(
    "/sessions/{session_id}",
    response_model=VerificationSession,
    summary="Get verification session details",
    description="Fetches the full session state including active rule profile, uploaded documents, extracted fields, and readiness scorecard.",
)
async def get_session(session_id: str):
    """Fetch session details by session_id."""

    session = session_store.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    return session


@router.post("/sessions/{session_id}/documents/upload")
async def upload_document(
    session_id: str,
    file: UploadFile = File(...),
):
    """Upload an image document, run OCR, and save the result to the session."""

    session = session_store.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    import os
    from datetime import datetime, timezone

    from app.models.schemas import ExtractedField, UploadedDocumentMetadata
    from app.services.document_detector import detect_document_type
    from app.services.field_extractor import extract_fields
    from app.services.ocr_service import extract_text_from_image
    from app.services.verification_service import run_name_verification

    temp_path = f"temp_{session_id}_{file.filename}"

    with open(temp_path, "wb") as temp_file:
        temp_file.write(file_bytes)

    try:
        extracted_text = extract_text_from_image(temp_path)
        extracted_fields = extract_fields(extracted_text)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    doc_id = f"doc_{session_id}_{len(session.documents) + 1}"

    document = UploadedDocumentMetadata(
        doc_id=doc_id,
        file_name=file.filename,
        detected_type=detect_document_type(extracted_text),
        uploaded_at=datetime.now(timezone.utc).isoformat(),
    )

    session.documents.append(document)

    for field_name, field_value in extracted_fields.items():
        extracted_field = ExtractedField(
            field_name=field_name,
            value=field_value,
            confidence=1.0,
            source_doc_id=doc_id,
        )

        session.extracted_fields.append(extracted_field)

    session.readiness.documents_checked = len(session.documents)
    session.readiness.fields_extracted = len(session.extracted_fields)

    session.readiness.required_documents_missing = [
        doc_type
        for doc_type in session.rule_config.required_documents
        if not any(
            doc.detected_type == doc_type
            for doc in session.documents
        )
    ]

    run_name_verification(session)

    session_store.update_session(session)

    return {
        "session_id": session_id,
        "file_name": file.filename,
        "doc_id": doc_id,
        "detected_type": document.detected_type,
        "extracted_text": extracted_text,
        "message": "Document uploaded, OCR completed, and session updated.",
    }

class ResolveDiscrepancyRequest(BaseModel):
    resolution_note: str


@router.post("/sessions/{session_id}/discrepancies/{discrepancy_id}/resolve")
async def resolve_discrepancy(
    session_id: str,
    discrepancy_id: str,
    request: ResolveDiscrepancyRequest,
):
    """Resolve a flagged discrepancy after human review."""

    session = session_store.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found.",
        )

    discrepancy = next(
        (
            item
            for item in session.discrepancies
            if item.id == discrepancy_id
        ),
        None,
    )

    if not discrepancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Discrepancy '{discrepancy_id}' not found.",
        )

    discrepancy.resolved = True
    discrepancy.resolution_note = request.resolution_note

    unresolved_mismatches = [
        item
        for item in session.discrepancies
        if not item.resolved
    ]

    session.readiness.potential_mismatches = len(unresolved_mismatches)

    if session.readiness.required_documents_missing:
        session.readiness.overall_status = ReadinessStatus.INCOMPLETE
        session.readiness.status_message = (
            "Some required documents are still missing."
        )
    elif unresolved_mismatches:
        session.readiness.overall_status = ReadinessStatus.ACTION_REQUIRED
        session.readiness.status_message = (
            f"{len(unresolved_mismatches)} document mismatch(es) require action."
        )
    else:
        session.readiness.overall_status = ReadinessStatus.READY_FOR_SUBMISSION
        session.readiness.status_message = (
            "All required documents are present, extracted information is "
            "consistent, and scholarship eligibility rules are satisfied."
        )

    session_store.update_session(session)

    return {
        "session_id": session_id,
        "discrepancy_id": discrepancy_id,
        "resolved": discrepancy.resolved,
        "resolution_note": discrepancy.resolution_note,
        "overall_status": session.readiness.overall_status,
        "message": "Discrepancy resolved successfully.",
    }



