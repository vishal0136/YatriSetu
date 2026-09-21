from typing import Any

from validation.rules.validate_database import DatabaseValidator


def run_post_update_validation() -> dict[str, Any]:
    """
    Run the existing deterministic database validator
    against DTMS_TEST after an authorized database update.

    The existing DatabaseValidator remains the single
    source of truth for validation.
    """

    validator = DatabaseValidator()

    validator.run(use_test_database=True)

    return {
        "dataset": "DTMS_TEST",
        "validation_status": (
            "PASS" if not validator.issues else "FAIL"
        ),
        "issue_count": len(validator.issues),
        "issues": validator.issues,
        "quality_observations": getattr(
            validator,
            "quality_observations",
            {},
        ),
    }

