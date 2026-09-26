from app.models.schemas import (
    DocumentType,
    ExtractedField,
    ReadinessScorecard,
    ScholarshipRuleConfig,
    MatchingThresholds,
    UploadedDocumentMetadata,
    VerificationSession,
)
from app.services.verification_service import run_name_verification


def create_test_session():
    rule_config = ScholarshipRuleConfig(
        scholarship_id="test-scholarship",
        name="Test Scholarship",
        description="Test rules",
        required_documents=[
            DocumentType.AADHAAR,
            DocumentType.MARKSHEET_12TH,
            DocumentType.INCOME_CERTIFICATE,
        ],
        income_ceiling=250000,
        min_academic_percentage=60,
        matching_thresholds=MatchingThresholds(
            auto_approve_threshold=0.98,
            human_review_threshold=0.80,
        ),
    )

    return VerificationSession(
        session_id="test_session",
        student_name="Hana Sharma",
        rule_config=rule_config,
        documents=[
            UploadedDocumentMetadata(
                doc_id="doc_aadhaar",
                file_name="aadhaar.png",
                detected_type=DocumentType.AADHAAR,
                uploaded_at="2026-09-26T00:00:00",
            ),
            UploadedDocumentMetadata(
                doc_id="doc_marksheet",
                file_name="marksheet.png",
                detected_type=DocumentType.MARKSHEET_12TH,
                uploaded_at="2026-09-26T00:00:00",
            ),
        ],
        extracted_fields=[
            ExtractedField(
                field_name="name",
                value="Hana Sharma",
                confidence=1.0,
                source_doc_id="doc_aadhaar",
            ),
            ExtractedField(
                field_name="name",
                value="Hana Sharm",
                confidence=1.0,
                source_doc_id="doc_marksheet",
            ),
        ],
        readiness=ReadinessScorecard(),
        created_at="2026-09-26T00:00:00",
    )


def test_resolved_name_discrepancy_is_not_recreated():
    session = create_test_session()

    run_name_verification(session)

    assert len(session.discrepancies) == 1

    discrepancy = session.discrepancies[0]
    discrepancy.resolved = True
    discrepancy.resolution_note = "Name variation reviewed by human reviewer."

    run_name_verification(session)

    assert len(session.discrepancies) == 1
    assert session.discrepancies[0].resolved is True
    assert (
        session.discrepancies[0].resolution_note
        == "Name variation reviewed by human reviewer."
    )

def test_resolved_name_discrepancy_counts_as_consistent():
    session = create_test_session()

    run_name_verification(session)

    assert len(session.discrepancies) == 1

    discrepancy = session.discrepancies[0]
    discrepancy.resolved = True
    discrepancy.resolution_note = "Name variation reviewed by human reviewer."

    run_name_verification(session)

    assert session.readiness.fields_consistent == 1
    assert session.readiness.potential_mismatches == 0

def test_resolve_discrepancy_rechecks_readiness():
    import asyncio

    from app.api.routes import ResolveDiscrepancyRequest, resolve_discrepancy

    session = create_test_session()

    from app.services.session_store import session_store
    session_store.update_session(session)

    run_name_verification(session)

    assert len(session.discrepancies) == 1

    discrepancy = session.discrepancies[0]

    result = asyncio.run(
        resolve_discrepancy(
            session_id=session.session_id,
            discrepancy_id=discrepancy.id,
            request=ResolveDiscrepancyRequest(
                resolution_note="Name variation reviewed by human reviewer."
            ),
        )
    )

    assert result["resolved"] is True
    assert result["overall_status"].value == "ACTION_REQUIRED"
    assert session.readiness.potential_mismatches == 0
