from typing import Any


VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}

REQUIRED_FIELDS = {
    "issue_summary",
    "primary_issue",
    "related_issues",
    "evidence",
    "unknowns",
    "recommended_action",
    "risk_level",
    "confidence",
    "proposed_changes",
    "requires_admin_approval",
}


def _recommendation_text(
    recommendation: dict[str, Any]
) -> str:
    """Combine model-generated textual fields."""

    fields = [
        "issue_summary",
        "primary_issue",
        "recommended_action",
    ]

    text_parts = []

    for field in fields:
        value = recommendation.get(field, "")

        if isinstance(value, str):
            text_parts.append(value)

    for field in [
        "related_issues",
        "evidence",
        "unknowns",
    ]:
        values = recommendation.get(field, [])

        if isinstance(values, list):
            text_parts.extend(
                str(value)
                for value in values
            )

    return " ".join(text_parts).lower()


def validate_recommendation(
    recommendation: dict[str, Any],
    validation_report: dict[str, Any],
) -> dict[str, Any]:

    errors = []
    warnings = []

    # ---------------------------------------------------------
    # 1. Required fields
    # ---------------------------------------------------------

    missing_fields = (
        REQUIRED_FIELDS
        - recommendation.keys()
    )

    if missing_fields:

        errors.append({
            "type": "MISSING_FIELD",
            "fields": sorted(
                missing_fields
            ),
        })

        return {
            "validation_status": "REJECT",
            "errors": errors,
            "warnings": warnings,
        }

    # ---------------------------------------------------------
    # 2. Confidence
    # ---------------------------------------------------------

    confidence = recommendation[
        "confidence"
    ]

    if not isinstance(
        confidence,
        (int, float),
    ):

        errors.append({
            "type": "INVALID_CONFIDENCE",
            "value": confidence,
        })

    elif not 0.0 <= confidence <= 1.0:

        errors.append({
            "type": "CONFIDENCE_OUT_OF_RANGE",
            "value": confidence,
        })

    # ---------------------------------------------------------
    # 3. Risk level
    # ---------------------------------------------------------

    risk_level = recommendation[
        "risk_level"
    ]

    if risk_level not in VALID_RISK_LEVELS:

        errors.append({
            "type": "INVALID_RISK_LEVEL",
            "value": risk_level,
        })

    # ---------------------------------------------------------
    # 4. Human approval
    # ---------------------------------------------------------

    if recommendation[
        "requires_admin_approval"
    ] is not True:

        errors.append({
            "type": "APPROVAL_BYPASS",
            "message": (
                "Admin approval must remain enabled."
            ),
        })

    # ---------------------------------------------------------
    # 5. Actual validation findings
    # ---------------------------------------------------------

    report_issues = validation_report.get(
        "issues",
        [],
    )

    report_rule_ids = {
        issue.get("rule_id")
        for issue in report_issues
        if issue.get("rule_id")
    }

    recommendation_text = (
        _recommendation_text(
            recommendation
        )
    )

    # ---------------------------------------------------------
    # 6. Primary issue grounding
    # ---------------------------------------------------------

    primary_issue = (
        recommendation[
            "primary_issue"
        ]
        .lower()
        .strip()
    )

    primary_grounded = False

    for issue in report_issues:

        description = issue.get(
            "description",
            "",
        ).lower()

        issue_type = issue.get(
            "issue_type",
            "",
        ).lower()

        rule_id = issue.get(
            "rule_id",
            "",
        ).lower()

        # Direct rule reference.
        if (
            rule_id
            and rule_id in primary_issue
        ):

            primary_grounded = True
            break

        # Controlled domain terms.
        domain_terms = set()

        if "latitude" in description:
            domain_terms.add("latitude")

        if "longitude" in description:
            domain_terms.add("longitude")

        if "coordinate" in description:
            domain_terms.add("coordinate")

        if "duplicate" in description:
            domain_terms.add("duplicate")

        if "sequence" in description:
            domain_terms.add("sequence")

        if "time" in description:
            domain_terms.add("time")

        if "reference" in description:
            domain_terms.add("reference")

        if "shape" in description:
            domain_terms.add("shape")

        if "service" in description:
            domain_terms.add("service")

        issue_concepts = {
            "invalid",
            "missing",
            "duplicate",
            "orphan",
            "inconsistent",
            "outside",
            "incorrect",
        }

        matched_domain_terms = [
            term
            for term in domain_terms
            if term in primary_issue
        ]

        matched_issue_concepts = [
            concept
            for concept in issue_concepts
            if concept in primary_issue
        ]

        if (
            matched_domain_terms
            and matched_issue_concepts
        ):

            primary_grounded = True
            break

        if (
            issue_type
            and issue_type in primary_issue
        ):

            primary_grounded = True
            break

    if (
        report_issues
        and not primary_grounded
    ):

        warnings.append({
            "type": (
                "PRIMARY_ISSUE_GROUNDING_REVIEW"
            ),
            "message": (
                "Primary issue could not be "
                "confidently grounded against "
                "the validation findings."
            ),
        })

    # ---------------------------------------------------------
    # 7. Quality observations
    # ---------------------------------------------------------

    quality_observations = (
        validation_report.get(
            "quality_observations",
            {},
        )
    )

    observation_fields = [
        "trip_headsign_missing",
        "direction_id_missing",
        "block_id_missing",
    ]

    for field in observation_fields:

        field_name = field.replace(
            "_missing",
            "",
        )

        if field_name in recommendation_text:

            corresponding_issue = any(
                field_name
                in issue.get(
                    "description",
                    "",
                ).lower()
                for issue in report_issues
            )

            if not corresponding_issue:

                warnings.append({
                    "type": (
                        "QUALITY_OBSERVATION_AS_ISSUE"
                    ),
                    "field": field,
                    "message": (
                        "The model referenced a "
                        "quality observation as "
                        "though it were a "
                        "validation issue."
                    ),
                })

    # ---------------------------------------------------------
    # 8. Proposed changes
    # ---------------------------------------------------------

    proposed_changes = (
        recommendation[
            "proposed_changes"
        ]
    )

    if not isinstance(
        proposed_changes,
        list,
    ):

        errors.append({
            "type": "INVALID_PROPOSED_CHANGES",
            "message": (
                "proposed_changes must be a list."
            ),
        })

        proposed_changes = []

    if (
        proposed_changes
        and not report_issues
    ):

        errors.append({
            "type": "UNSUPPORTED_CHANGE",
            "message": (
                "Proposed changes exist but "
                "the validation report contains "
                "no issues."
            ),
        })

    # ---------------------------------------------------------
    # 9. Validate each proposed change
    #
    # Database changes require explicit evidence.
    # ---------------------------------------------------------

    required_change_fields = {
        "table",
        "record_id",
        "field",
        "old_value",
        "proposed_value",
        "evidence_source",
    }

    for index, change in enumerate(
        proposed_changes
    ):

        if not isinstance(
            change,
            dict,
        ):

            errors.append({
                "type": "INVALID_CHANGE_OBJECT",
                "change_index": index,
            })

            continue

        missing_change_fields = (
            required_change_fields
            - change.keys()
        )

        if missing_change_fields:

            errors.append({
                "type": "INCOMPLETE_PROPOSED_CHANGE",
                "change_index": index,
                "fields": sorted(
                    missing_change_fields
                ),
            })

            continue

        # A replacement value must be explicitly
        # supported by an evidence source.
        if not change.get(
            "evidence_source"
        ):

            errors.append({
                "type": "MISSING_EVIDENCE_SOURCE",
                "change_index": index,
            })

    # ---------------------------------------------------------
    # 10. Final status
    # ---------------------------------------------------------

    if errors:

        status = "REJECT"

    elif warnings:

        status = "REVIEW"

    else:

        status = "PASS"

    result = {
        "validation_status": status,
        "errors": errors,
        "warnings": warnings,
        "quality_observations_checked": (
            quality_observations
        ),
        "report_rule_ids": sorted(
            report_rule_ids
        ),
    }

    # ---------------------------------------------------------
    # 11. Safety-approved change set
    #
    # IMPORTANT:
    # Only a fully PASSed recommendation can produce
    # approved_changes.
    #
    # REVIEW and REJECT never produce this field.
    # ---------------------------------------------------------

    if status == "PASS":

        result[
            "approved_changes"
        ] = proposed_changes.copy()

    return result


if __name__ == "__main__":
    print(
        "Recommendation Validator "
        "loaded successfully."
    )
