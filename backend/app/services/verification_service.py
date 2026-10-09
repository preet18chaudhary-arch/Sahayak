
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
        income_value = (
            str(income_fields[0].value).strip()
            if income_fields and income_fields[0].value is not None
            else ""
        )

        try:
            if not income_value:
                raise ValueError("Income is missing")

            income = float(
                income_value.replace(",", "").replace("₹", "").strip()
            )
        except (ValueError, TypeError):
            eligible = False
            reasons.append(
                "Income information could not be verified. "
                "Please check the income certificate."
            )
        else:
            if income > income_ceiling:
                eligible = False
                reasons.append(
                    f"Income exceeds the allowed scholarship limit of "
                    f"{income_ceiling:,.0f}."
                )

    if minimum_percentage is not None:
        percentage_value = (
            str(percentage_fields[0].value).strip()
            if percentage_fields and percentage_fields[0].value is not None
            else ""
        )

        try:
            if not percentage_value:
                raise ValueError("Academic percentage is missing")

            percentage = float(
                percentage_value.replace("%", "").strip()
            )
        except (ValueError, TypeError):
            eligible = False
            reasons.append(
                "Academic percentage could not be verified. "
                "Please check the marksheet."
            )
        else:
            if percentage < minimum_percentage:
                eligible = False
                reasons.append(
                    f"Academic percentage {percentage}% is below the "
                    f"required {minimum_percentage}%."
                )

    return eligible, reasons
    
def run_name_verification(session) -> None:
    """Run document consistency and scholarship eligibility checks."""

    resolved_discrepancies = [
        discrepancy
        for discrepancy in session.discrepancies
        if discrepancy.resolved
    ]
    session.discrepancies = resolved_discrepancies

    name_consistent_count, _ = check_name_consistency(session)
    dob_consistent_count, _ = check_dob_consistency(session)

    eligible, eligibility_reasons = check_eligibility_rules(session)

    session.readiness.fields_consistent = (
        name_consistent_count + dob_consistent_count
    )

    unresolved_mismatches = [
        discrepancy
        for discrepancy in session.discrepancies
        if not discrepancy.resolved
    ]
    session.readiness.potential_mismatches = len(unresolved_mismatches)

    if session.readiness.required_documents_missing:
        session.readiness.overall_status = ReadinessStatus.INCOMPLETE
        session.readiness.status_message = (
            "Some required documents are still missing."
        )
        return

    thresholds = session.rule_config.matching_thresholds

    action_required = [
        discrepancy
        for discrepancy in unresolved_mismatches
        if discrepancy.similarity_score < thresholds.human_review_threshold
    ]

    review_required = [
        discrepancy
        for discrepancy in unresolved_mismatches
        if (
            thresholds.human_review_threshold
            <= discrepancy.similarity_score
            < thresholds.auto_approve_threshold
        )
    ]

    if not eligible:
        session.readiness.overall_status = ReadinessStatus.ACTION_REQUIRED
        reasons = list(eligibility_reasons)

        if action_required:
            reasons.append(
                f"{len(action_required)} document mismatch(es) require action."
            )
        if review_required:
            reasons.append(
                f"{len(review_required)} document mismatch(es) require human review."
            )

        session.readiness.status_message = " ".join(reasons)
        return

    if action_required:
        session.readiness.overall_status = ReadinessStatus.ACTION_REQUIRED
        session.readiness.status_message = (
            f"{len(action_required)} document mismatch(es) require action."
        )
        return

    if review_required:
        session.readiness.overall_status = ReadinessStatus.IN_REVIEW
        session.readiness.status_message = (
            f"{len(review_required)} document mismatch(es) require human review."
        )
        return

    session.readiness.overall_status = ReadinessStatus.READY_FOR_SUBMISSION
    session.readiness.status_message = (
        "All required documents are present, extracted information is "
        "consistent, and scholarship eligibility rules are satisfied."
    )

