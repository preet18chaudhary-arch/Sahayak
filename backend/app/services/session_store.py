import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.models.schemas import (
    ReadinessScorecard,
    ReadinessStatus,
    ScholarshipRuleConfig,
    VerificationSession,
)


class InMemorySessionStore:
    """
    Lightweight, in-memory repository for verification sessions.
    Ideal for hackathons: zero-config, thread-safe dictionary, and fully explainable.
    """

    def __init__(self):
        self._sessions: Dict[str, VerificationSession] = {}

    def create_session(
        self,
        student_name: Optional[str],
        rule_config: ScholarshipRuleConfig,
    ) -> VerificationSession:
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc).isoformat()

        # Build initial readiness scorecard based on the specific scholarship's rules
        initial_scorecard = ReadinessScorecard(
            documents_checked=0,
            fields_extracted=0,
            fields_consistent=0,
            potential_mismatches=0,
            required_documents_missing=[doc.value for doc in rule_config.required_documents],
            overall_status=ReadinessStatus.INCOMPLETE,
            status_message=f"Session created for {rule_config.name}. Please upload the {len(rule_config.required_documents)} required documents.",
        )

        session = VerificationSession(
            session_id=session_id,
            student_name=student_name,
            rule_config=rule_config,
            documents=[],
            extracted_fields=[],
            discrepancies=[],
            readiness=initial_scorecard,
            created_at=now,
        )

        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[VerificationSession]:
        return self._sessions.get(session_id)

    def update_session(self, session: VerificationSession) -> VerificationSession:
        self._sessions[session.session_id] = session
        return session

    def list_sessions(self) -> List[VerificationSession]:
        return list(self._sessions.values())


# Singleton instance shared across requests
session_store = InMemorySessionStore()
