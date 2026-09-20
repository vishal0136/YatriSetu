from datetime import datetime, timezone
from typing import Any


ALLOWED_TABLES = {
    "stops",
}

ALLOWED_FIELDS = {
    "stops": {
        "stop_lat",
        "stop_lon",
    },
}


def _blocked(
    reason: str,
    admin_decision: str,
    admin_id: str,
    timestamp: str,
    **extra,
) -> dict[str, Any]:

    return {
        "authorization_status": "BLOCKED",
        "reason": reason,
        "admin_decision": admin_decision,
        "admin_id": admin_id,
        "timestamp": timestamp,
        **extra,
    }


def authorize_database_change(
    recommendation: dict[str, Any],
    safety_validation: dict[str, Any],
    admin_decision: str,
    admin_id: str,
) -> dict[str, Any]:

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    # --------------------------------------------------------
    # Gate 1: Safety validation
    # --------------------------------------------------------

    if safety_validation.get(
        "validation_status"
    ) != "PASS":

        return _blocked(
            "Recommendation did not pass "
            "deterministic safety validation.",
            admin_decision,
            admin_id,
            timestamp,
        )

    # --------------------------------------------------------
    # Gate 2: Explicit administrator approval
    # --------------------------------------------------------

    if admin_decision != "APPROVE":

        return _blocked(
            "Explicit administrator approval is required.",
            admin_decision,
            admin_id,
            timestamp,
        )

    # --------------------------------------------------------
    # Gate 3: Mandatory approval policy
    # --------------------------------------------------------

    if recommendation.get(
        "requires_admin_approval"
    ) is not True:

        return _blocked(
            "Recommendation does not satisfy "
            "mandatory approval policy.",
            admin_decision,
            admin_id,
            timestamp,
        )

    # --------------------------------------------------------
    # Gate 4: Explicit proposed change required
    # --------------------------------------------------------

    proposed_changes = recommendation.get(
        "proposed_changes"
    )

    if not isinstance(
        proposed_changes,
        list
    ) or not proposed_changes:

        return _blocked(
            "No explicit database change exists "
            "in the recommendation.",
            admin_decision,
            admin_id,
            timestamp,
        )

    # --------------------------------------------------------
    # Gate 5: Safety-approved change list must exist
    # --------------------------------------------------------

    safety_approved_changes = (
        safety_validation.get(
            "approved_changes"
        )
    )

    if safety_approved_changes is None:

        return _blocked(
            "Safety validation did not provide "
            "an approved change set.",
            admin_decision,
            admin_id,
            timestamp,
        )

    if safety_approved_changes != proposed_changes:

        return _blocked(
            "Proposed changes do not exactly match "
            "the safety-approved change set.",
            admin_decision,
            admin_id,
            timestamp,
        )

    # --------------------------------------------------------
    # Gate 6: Validate each change
    # --------------------------------------------------------

    required_fields = {
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
            dict
        ):

            return _blocked(
                "Proposed database change "
                "must be an object.",
                admin_decision,
                admin_id,
                timestamp,
                change_index=index,
            )

        missing_fields = (
            required_fields
            - change.keys()
        )

        if missing_fields:

            return _blocked(
                "Proposed database change "
                "is incomplete.",
                admin_decision,
                admin_id,
                timestamp,
                change_index=index,
                missing_fields=sorted(
                    missing_fields
                ),
            )

        # ----------------------------------------------------
        # Gate 7: Table allowlist
        # ----------------------------------------------------

        table = change["table"]

        if table not in ALLOWED_TABLES:

            return _blocked(
                f"Table '{table}' is not authorized "
                "for automated correction.",
                admin_decision,
                admin_id,
                timestamp,
                change_index=index,
            )

        # ----------------------------------------------------
        # Gate 8: Field allowlist
        # ----------------------------------------------------

        field = change["field"]

        if field not in ALLOWED_FIELDS.get(
            table,
            set(),
        ):

            return _blocked(
                f"Field '{field}' is not authorized "
                f"for table '{table}'.",
                admin_decision,
                admin_id,
                timestamp,
                change_index=index,
            )

        # ----------------------------------------------------
        # Gate 9: Values must actually differ
        # ----------------------------------------------------

        if change["old_value"] == change[
            "proposed_value"
        ]:

            return _blocked(
                "Proposed value is identical "
                "to the current value.",
                admin_decision,
                admin_id,
                timestamp,
                change_index=index,
            )

        # ----------------------------------------------------
        # Gate 10: Evidence source required
        # ----------------------------------------------------

        if not change.get(
            "evidence_source"
        ):

            return _blocked(
                "An evidence source is required "
                "for every database change.",
                admin_decision,
                admin_id,
                timestamp,
                change_index=index,
            )

    # --------------------------------------------------------
    # Authorized
    #
    # IMPORTANT:
    # This function does NOT execute SQL.
    # --------------------------------------------------------

    return {
        "authorization_status": "AUTHORIZED",
        "reason": (
            "Database change passed deterministic safety "
            "validation, exactly matched the safety-approved "
            "change set, passed the table/field allowlists, "
            "and received explicit administrator approval."
        ),
        "authorized_changes": proposed_changes,
        "admin_decision": admin_decision,
        "admin_id": admin_id,
        "timestamp": timestamp,
    }


if __name__ == "__main__":
    print(
        "Change Authorization module loaded successfully."
    )
