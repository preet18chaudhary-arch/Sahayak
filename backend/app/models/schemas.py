from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    AADHAAR = "aadhaar"
    MARKSHEET_10TH = "marksheet_10th"
    MARKSHEET_12TH = "marksheet_12th"
    INCOME_CERTIFICATE = "income_certificate"
    CASTE_CERTIFICATE = "caste_certificate"
    DOMICILE_CERTIFICATE = "domicile_certificate"
    BANK_PASSBOOK = "bank_passbook"
    OTHER = "other"


class MatchingThresholds(BaseModel):
    """
    Configurable fuzzy matching thresholds.
    - auto_approve_threshold: >= this score is treated as an exact match.
    - human_review_threshold: >= this score flags as a minor typo requiring human review.
      Scores below human_review_threshold are treated as hard mismatches.
    """
    auto_approve_threshold: float = Field(
        default=0.98,
        ge=0.0,
        le=1.0,
        description="Threshold at or above which values are automatically considered identical (e.g. 0.98 = 98%)"
    )
    human_review_threshold: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
        description="Threshold below which values are considered incompatible mismatches rather than typos"
    )


class ScholarshipRuleConfig(BaseModel):
    """
    Configurable rule profile for a scholarship scheme.
    Enables Sahayak to support multiple scholarships without hard-coded criteria.
    """
    scholarship_id: str = Field(..., description="Unique slug for the scholarship")
    name: str = Field(..., description="Display title of the scholarship")
    description: str = Field(..., description="Brief summary of eligibility rules")
    required_documents: List[DocumentType] = Field(
        ...,
        description="List of document types mandatory for this scholarship"
    )
    income_ceiling: Optional[float] = Field(
        default=None,
        description="Maximum annual family income in INR (None if not applicable)"
    )
    min_academic_percentage: Optional[float] = Field(
        default=None,
        description="Minimum marks aggregate percentage required (None if not applicable)"
    )
    matching_thresholds: MatchingThresholds = Field(
        default_factory=MatchingThresholds,
        description="Thresholds for auto-approval vs human review"
    )


class ExtractedField(BaseModel):
    """A single field extracted from an uploaded document."""
    field_name: str
    value: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_doc_id: Optional[str] = None


class Discrepancy(BaseModel):
    """A cross-document mismatch or spelling variation flagged for review."""
    id: str
    field_name: str
    doc_a_type: DocumentType
    doc_b_type: DocumentType
    value_a: str
    value_b: str
    similarity_score: float
    explanation: str
    resolved: bool = False
    resolution_note: Optional[str] = None


class ReadinessStatus(str, Enum):
    READY_FOR_SUBMISSION = "READY_FOR_SUBMISSION"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    INCOMPLETE = "INCOMPLETE"
    IN_REVIEW = "IN_REVIEW"


class ReadinessScorecard(BaseModel):
    """Summary metrics presented to the student and reviewer."""
    documents_checked: int = 0
    fields_extracted: int = 0
    fields_consistent: int = 0
    potential_mismatches: int = 0
    required_documents_missing: List[str] = []
    overall_status: ReadinessStatus = ReadinessStatus.INCOMPLETE
    status_message: str = "Session initialized. Awaiting document uploads."


class UploadedDocumentMetadata(BaseModel):
    """Metadata for an uploaded file."""
    doc_id: str
    file_name: str
    detected_type: Optional[DocumentType] = None
    uploaded_at: str


class VerificationSession(BaseModel):
    """Full session state capturing documents, rules, and verification outputs."""
    session_id: str
    student_name: Optional[str] = None
    rule_config: ScholarshipRuleConfig
    documents: List[UploadedDocumentMetadata] = []
    extracted_fields: List[ExtractedField] = []
    discrepancies: List[Discrepancy] = []
    readiness: ReadinessScorecard
    created_at: str


class CreateSessionRequest(BaseModel):
    """Payload to create a new verification session."""
    student_name: Optional[str] = "Hana Sharma"
    scholarship_id: Optional[str] = "merit-cum-means"
    custom_rules: Optional[ScholarshipRuleConfig] = None
