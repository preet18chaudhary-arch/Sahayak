from typing import Dict, List, Optional
from app.models.schemas import DocumentType, MatchingThresholds, ScholarshipRuleConfig

# Preset demo scholarship schemes with configurable rules
_PRESET_SCHOLARSHIPS: Dict[str, ScholarshipRuleConfig] = {
    "merit-cum-means": ScholarshipRuleConfig(
        scholarship_id="merit-cum-means",
        name="National Merit-cum-Means Scholarship",
        description="Merit scholarship for economically disadvantaged students with family income <= ₹2.5 LPA and marks >= 60%.",
        required_documents=[
            DocumentType.AADHAAR,
            DocumentType.MARKSHEET_12TH,
            DocumentType.INCOME_CERTIFICATE,
        ],
        income_ceiling=250000.0,
        min_academic_percentage=60.0,
        matching_thresholds=MatchingThresholds(
            auto_approve_threshold=0.98,
            human_review_threshold=0.80,
        ),
    ),
    "post-matric-sc-st": ScholarshipRuleConfig(
        scholarship_id="post-matric-sc-st",
        name="Post-Matric Scholarship (SC/ST/OBC)",
        description="Government social welfare scholarship with family income cap of ₹8.0 LPA and minimum 50% aggregate.",
        required_documents=[
            DocumentType.AADHAAR,
            DocumentType.MARKSHEET_10TH,
            DocumentType.CASTE_CERTIFICATE,
            DocumentType.INCOME_CERTIFICATE,
        ],
        income_ceiling=800000.0,
        min_academic_percentage=50.0,
        matching_thresholds=MatchingThresholds(
            auto_approve_threshold=0.95,
            human_review_threshold=0.75,
        ),
    ),
    "general-fellowship": ScholarshipRuleConfig(
        scholarship_id="general-fellowship",
        name="National Higher Education Excellence Fellowship",
        description="Merit-only fellowship for high-achieving undergraduate students. Minimum 75% marks with direct bank transfer verification.",
        required_documents=[
            DocumentType.AADHAAR,
            DocumentType.MARKSHEET_12TH,
            DocumentType.BANK_PASSBOOK,
        ],
        income_ceiling=None,  # No income limit
        min_academic_percentage=75.0,
        matching_thresholds=MatchingThresholds(
            auto_approve_threshold=0.98,
            human_review_threshold=0.85,
        ),
    ),
}


def get_available_scholarships() -> List[ScholarshipRuleConfig]:
    """Returns all pre-registered scholarship rule configurations."""
    return list(_PRESET_SCHOLARSHIPS.values())


def get_scholarship_rule_by_id(scholarship_id: str) -> Optional[ScholarshipRuleConfig]:
    """Retrieves a specific scholarship rule configuration by its slug."""
    return _PRESET_SCHOLARSHIPS.get(scholarship_id)
