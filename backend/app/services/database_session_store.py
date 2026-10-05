import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select

from app.database.database import SessionLocal
from app.database.models import (
    SessionModel,
    DocumentModel,
    ExtractedFieldModel,
    DiscrepancyModel,
)

from app.models.schemas import (
    ReadinessScorecard,
    ScholarshipRuleConfig,
    VerificationSession,
    UploadedDocumentMetadata,
    ExtractedField,
    Discrepancy,
    DocumentType,
)


class DatabaseSessionStore:
    """Persistent session store backed by SQLite."""

    def create_session(
        self,
        student_name: Optional[str],
        rule_config: ScholarshipRuleConfig,
    ) -> VerificationSession:

        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        initial_scorecard = ReadinessScorecard(
            documents_checked=0,
            fields_extracted=0,
            fields_consistent=0,
            potential_mismatches=0,
            required_documents_missing=[
                doc.value for doc in rule_config.required_documents
            ],
            overall_status="INCOMPLETE",
            status_message=(
                f"Session created for {rule_config.name}. "
                f"Please upload the "
                f"{len(rule_config.required_documents)} required documents."
            ),
        )

        session = VerificationSession(
            session_id=session_id,
            student_name=student_name,
            rule_config=rule_config,
            documents=[],
            extracted_fields=[],
            discrepancies=[],
            readiness=initial_scorecard,
            created_at=now.isoformat(),
        )

        db = SessionLocal()

        try:
            db_session = SessionModel(
                session_id=session_id,
                student_name=student_name,
                scholarship_id=rule_config.scholarship_id,
                rule_config=json.dumps(
                    rule_config.model_dump(),
                    default=str,
                ),
                readiness=json.dumps(
                    initial_scorecard.model_dump(),
                    default=str,
                ),
                created_at=now,
            )

            db.add(db_session)
            db.commit()

            return session

        finally:
            db.close()

    def get_session(
        self,
        session_id: str,
    ) -> Optional[VerificationSession]:

        db = SessionLocal()

        try:
            db_session = db.scalar(
                select(SessionModel).where(
                    SessionModel.session_id == session_id
                )
            )

            if db_session is None:
                return None

            return self._to_schema(db, db_session)

        finally:
            db.close()

    def update_session(
        self,
        session: VerificationSession,
    ) -> VerificationSession:

        db = SessionLocal()

        try:
            db_session = db.scalar(
                select(SessionModel).where(
                    SessionModel.session_id == session.session_id
                )
            )

            if db_session is None:
                raise ValueError(
                    f"Session {session.session_id} does not exist"
                )

            db_session.student_name = session.student_name

            db_session.rule_config = json.dumps(
                session.rule_config.model_dump(),
                default=str,
            )

            db_session.readiness = json.dumps(
                session.readiness.model_dump(),
                default=str,
            )

            # Remove old child records.
            db.query(DocumentModel).filter(
                DocumentModel.session_id == session.session_id
            ).delete()

            db.query(ExtractedFieldModel).filter(
                ExtractedFieldModel.session_id == session.session_id
            ).delete()

            db.query(DiscrepancyModel).filter(
                DiscrepancyModel.session_id == session.session_id
            ).delete()

            # Save documents.
            for document in session.documents:

                detected_type = None

                if document.detected_type is not None:
                    if hasattr(document.detected_type, "value"):
                        detected_type = document.detected_type.value
                    else:
                        detected_type = str(document.detected_type)

                uploaded_at = None

                if document.uploaded_at:
                    try:
                        uploaded_at = datetime.fromisoformat(
                            document.uploaded_at.replace("Z", "+00:00")
                        )
                    except ValueError:
                        uploaded_at = datetime.now(timezone.utc)

                if uploaded_at is None:
                    uploaded_at = datetime.now(timezone.utc)

                db.add(
                    DocumentModel(
                        doc_id=document.doc_id,
                        session_id=session.session_id,
                        file_name=document.file_name,
                        detected_type=detected_type,
                        uploaded_at=uploaded_at,
                    )
                )

            # Save extracted fields.
            for field in session.extracted_fields:

                db.add(
                    ExtractedFieldModel(
                        session_id=session.session_id,
                        field_name=field.field_name,
                        value=str(field.value),
                        confidence=field.confidence,
                        source_doc_id=field.source_doc_id,
                    )
                )

            # Save discrepancies.
            for discrepancy in session.discrepancies:

                doc_a_type = (
                    discrepancy.doc_a_type.value
                    if hasattr(discrepancy.doc_a_type, "value")
                    else str(discrepancy.doc_a_type)
                )

                doc_b_type = (
                    discrepancy.doc_b_type.value
                    if hasattr(discrepancy.doc_b_type, "value")
                    else str(discrepancy.doc_b_type)
                )

                db.add(
                    DiscrepancyModel(
                        session_id=session.session_id,
                        discrepancy_id=discrepancy.id,
                        field_name=discrepancy.field_name,
                        doc_a_type=doc_a_type,
                        doc_b_type=doc_b_type,
                        value_a=str(discrepancy.value_a),
                        value_b=str(discrepancy.value_b),
                        similarity_score=discrepancy.similarity_score,
                        explanation=discrepancy.explanation,
                        resolved=discrepancy.resolved,
                        resolution_note=discrepancy.resolution_note,
                    )
                )

            db.commit()

            return session

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def list_sessions(self) -> List[VerificationSession]:

        db = SessionLocal()

        try:
            db_sessions = db.scalars(
                select(SessionModel).order_by(
                    SessionModel.created_at.desc()
                )
            ).all()

            return [
                self._to_schema(db, db_session)
                for db_session in db_sessions
            ]

        finally:
            db.close()

    def _to_schema(
        self,
        db,
        db_session: SessionModel,
    ) -> VerificationSession:

        rule_config_data = json.loads(db_session.rule_config)
        readiness_data = json.loads(db_session.readiness)

        rule_config = ScholarshipRuleConfig.model_validate(
            rule_config_data
        )

        readiness = ReadinessScorecard.model_validate(
            readiness_data
        )

        # Restore documents.
        db_documents = db.scalars(
            select(DocumentModel).where(
                DocumentModel.session_id == db_session.session_id
            )
        ).all()

        documents = []

        for document in db_documents:

            detected_type = None

            if document.detected_type:
                try:
                    detected_type = DocumentType(document.detected_type)
                except ValueError:
                    detected_type = None

            documents.append(
                UploadedDocumentMetadata(
                    doc_id=document.doc_id,
                    file_name=document.file_name,
                    detected_type=detected_type,
                    uploaded_at=document.uploaded_at.isoformat(),
                )
            )

        # Restore extracted fields.
        db_fields = db.scalars(
            select(ExtractedFieldModel).where(
                ExtractedFieldModel.session_id == db_session.session_id
            )
        ).all()

        extracted_fields = [
            ExtractedField(
                field_name=field.field_name,
                value=field.value,
                confidence=field.confidence,
                source_doc_id=field.source_doc_id,
            )
            for field in db_fields
        ]

        # Restore discrepancies.
        db_discrepancies = db.scalars(
            select(DiscrepancyModel).where(
                DiscrepancyModel.session_id == db_session.session_id
            )
        ).all()

        discrepancies = []

        for discrepancy in db_discrepancies:

            try:
                doc_a_type = DocumentType(discrepancy.doc_a_type)
            except ValueError:
                doc_a_type = DocumentType.OTHER

            try:
                doc_b_type = DocumentType(discrepancy.doc_b_type)
            except ValueError:
                doc_b_type = DocumentType.OTHER

            discrepancies.append(
                Discrepancy(
                    id=discrepancy.discrepancy_id,
                    field_name=discrepancy.field_name,
                    doc_a_type=doc_a_type,
                    doc_b_type=doc_b_type,
                    value_a=discrepancy.value_a,
                    value_b=discrepancy.value_b,
                    similarity_score=discrepancy.similarity_score,
                    explanation=discrepancy.explanation,
                    resolved=discrepancy.resolved,
                    resolution_note=discrepancy.resolution_note,
                )
            )

        return VerificationSession(
            session_id=db_session.session_id,
            student_name=db_session.student_name,
            rule_config=rule_config,
            documents=documents,
            extracted_fields=extracted_fields,
            discrepancies=discrepancies,
            readiness=readiness,
            created_at=db_session.created_at.isoformat(),
        )


session_store = DatabaseSessionStore()
