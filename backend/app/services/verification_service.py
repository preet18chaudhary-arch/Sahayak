from difflib import SequenceMatcher

from app.models.schemas import Discrepancy, ReadinessStatus


def calculate_similarity(value_a: str, value_b: str) -> float:
    """Return a similarity score between two text values from 0.0 to 1.0."""

    normalized_a = value_a.strip().lower()
    normalized_b = value_b.strip().lower()

    return SequenceMatcher(
        None,
        normalized_a,
        normalized_b
    ).ratio()


def check_name_consistency(session) -> tuple[int, int]:
    """Check whether extracted name values are consistent across documents."""

    name_fields = [
        field
        for field in session.extracted_fields
        if field.field_name == "name"
    ]

    if len(name_fields) < 2:
        return 0, 0

    reference_name = name_fields[0].value
    reference_doc_id = name_fields[0].source_doc_id

    consistent_count = 0
    mismatch_count = 0

    auto_approve_threshold = (
        session.rule_config.matching_thresholds.auto_approve_threshold
    )
    human_review_threshold = (
        session.rule_config.matching_thresholds.human_review_threshold
    )

    for field in name_fields[1:]:
        similarity = calculate_similarity(reference_name, field.value)

        if similarity >= auto_approve_threshold:
            consistent_count += 1
            continue

        mismatch_count += 1

        reference_doc = next(
            (
                doc
                for doc in session.documents
                if doc.doc_id == reference_doc_id
            ),
            None,
        )

        current_doc = next(
            (
                doc
                for doc in session.documents
                if doc.doc_id == field.source_doc_id
            ),
            None,
        )

        if reference_doc and current_doc:
            if similarity >= human_review_threshold:
                explanation = (
                    "Name values are similar but require human review."
                )
            else:
                explanation = (
                    "Name values differ significantly and require action."
                )

            session.discrepancies.append(
                Discrepancy(
                    id=f"disc_{session.session_id}_{len(session.discrepancies) + 1}",
                    field_name="name",
                    doc_a_type=reference_doc.detected_type,
                    doc_b_type=current_doc.detected_type,
                    value_a=reference_name,
                    value_b=field.value,
                    similarity_score=round(similarity, 3),
                    explanation=explanation,
                )
            )

    return consistent_count, mismatch_count


def normalize_date_of_birth(value: str) -> str:
    """Normalize a date of birth so common separators are treated equally."""

    return value.strip().replace("-", "/")


def check_dob_consistency(session) -> tuple[int, int]:
    """Check whether date of birth values are exactly consistent across documents."""

    dob_fields = [
        field
        for field in session.extracted_fields
        if field.field_name == "date_of_birth"
    ]

    if len(dob_fields) < 2:
        return 0, 0

    reference_dob = normalize_date_of_birth(dob_fields[0].value)
    reference_doc_id = dob_fields[0].source_doc_id

    consistent_count = 0
    mismatch_count = 0

    for field in dob_fields[1:]:
        current_dob = normalize_date_of_birth(field.value)

        if reference_dob == current_dob:
            consistent_count += 1
            continue

        mismatch_count += 1

        reference_doc = next(
            (
                doc
                for doc in session.documents
                if doc.doc_id == reference_doc_id
            ),
            None,
        )

        current_doc = next(
            (
                doc
                for doc in session.documents
                if doc.doc_id == field.source_doc_id
            ),
            None,
        )

        if reference_doc and current_doc:
            session.discrepancies.append(
                Discrepancy(
                    id=f"disc_{session.session_id}_{len(session.discrepancies) + 1}",
                    field_name="date_of_birth",
                    doc_a_type=reference_doc.detected_type,
                    doc_b_type=current_doc.detected_type,
                    value_a=reference_dob,
                    value_b=current_dob,
                    similarity_score=0.0,
                    explanation=(
                        "Date of birth values do not match and require action."
                    ),
                )
            )

    return consistent_count, mismatch_count


def check_eligibility_rules(session) -> tuple[bool, list[str]]:
    """Check scholarship eligibility rules against extracted fields."""

    reasons = []
    eligible = True

    income_ceiling = session.rule_config.income_ceiling
    minimum_percentage = session.rule_config.min_academic_percentage

    income_fields = [
        field
        for field in session.extracted_fields
        if field.field_name == "income"
    ]

    percentage_fields = [
        field
        for field in session.extracted_fields
        if field.field_name == "percentage"
    ]

    if income_ceiling is not None:
        if not income_fields:
            eligible = False
            reasons.append("Income information could not be verified.")
        else:
            income = float(income_fields[0].value)

            if income > income_ceiling:
                eligible = False
                reasons.append(
                    f"Income exceeds the allowed scholarship limit of "
                    f"{income_ceiling:,.0f}."
                )

    if minimum_percentage is not None:
        if not percentage_fields:
            eligible = False
            reasons.append("Academic percentage could not be verified.")
        else:
            percentage = float(percentage_fields[0].value)

            if percentage < minimum_percentage:
                eligible = False
                reasons.append(
                    f"Academic percentage {percentage}% is below the "
                    f"required {minimum_percentage}%."
                )

    return eligible, reasons


def run_name_verification(session) -> None:
    """Run document consistency and scholarship eligibility checks."""

    session.discrepancies = []

    name_consistent_count, name_mismatch_count = check_name_consistency(session)
    dob_consistent_count, dob_mismatch_count = check_dob_consistency(session)

    eligible, eligibility_reasons = check_eligibility_rules(session)

    session.readiness.fields_consistent = (
        name_consistent_count + dob_consistent_count
    )

    session.readiness.potential_mismatches = (
        name_mismatch_count + dob_mismatch_count
    )

    missing_documents = session.readiness.required_documents_missing

    if missing_documents:
        session.readiness.overall_status = ReadinessStatus.INCOMPLETE
        session.readiness.status_message = (
            "Some required documents are still missing."
        )
        return

    action_required_mismatches = [
        discrepancy
        for discrepancy in session.discrepancies
        if discrepancy.similarity_score
        < session.rule_config.matching_thresholds.human_review_threshold
    ]

    review_required_mismatches = [
        discrepancy
        for discrepancy in session.discrepancies
        if (
            discrepancy.similarity_score
            >= session.rule_config.matching_thresholds.human_review_threshold
            and discrepancy.similarity_score
            < session.rule_config.matching_thresholds.auto_approve_threshold
        )
    ]

    if not eligible:
        session.readiness.overall_status = ReadinessStatus.ACTION_REQUIRED

        reasons = list(eligibility_reasons)

        if action_required_mismatches:
            reasons.append(
                f"{len(action_required_mismatches)} document mismatch(es) require action."
            )

        if review_required_mismatches:
            reasons.append(
                f"{len(review_required_mismatches)} document mismatch(es) require human review."
            )

        session.readiness.status_message = " ".join(reasons)
        return

    if action_required_mismatches:
        session.readiness.overall_status = ReadinessStatus.ACTION_REQUIRED
        session.readiness.status_message = (
            f"{len(action_required_mismatches)} document mismatch(es) require action."
        )
        return

    if review_required_mismatches:
        session.readiness.overall_status = ReadinessStatus.IN_REVIEW
        session.readiness.status_message = (
            f"{len(review_required_mismatches)} document mismatch(es) require human review."
        )
        return

    session.readiness.overall_status = ReadinessStatus.READY_FOR_SUBMISSION
    session.readiness.status_message = (
        "All required documents are present, extracted information is "
        "consistent, and scholarship eligibility rules are satisfied."
    )
