
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
