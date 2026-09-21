from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from backend.app.ai.services.db_evidence import create_test_engine


ALLOWED_TABLES = {
    "stops",
}

ALLOWED_FIELDS = {
    "stops": {
        "stop_lat",
        "stop_lon",
    },
}


def execute_authorized_change(
    authorization_result: dict[str, Any],
    db_engine: Engine | None = None,
) -> dict[str, Any]:
    """
    Execute an already-authorized database change.

    Safety properties:
    - Requires authorization_status == AUTHORIZED.
    - Uses DTMS_TEST by default.
    - Verifies old_value before UPDATE.
    - Executes inside a transaction.
    - Verifies the new value after UPDATE.
    - Rolls back on any failure.
    - Does not accept a raw recommendation.
    """

    if authorization_result.get("authorization_status") != "AUTHORIZED":
        return {
            "transaction_status": "BLOCKED",
            "reason": "Database change is not authorized.",
        }

    authorized_changes = authorization_result.get(
        "authorized_changes"
    )

    if not isinstance(authorized_changes, list) or not authorized_changes:
        return {
            "transaction_status": "BLOCKED",
            "reason": "No authorized changes were provided.",
        }

    if db_engine is None:
        db_engine = create_test_engine()

    executed_changes = []

    try:
        with db_engine.begin() as connection:

            for index, change in enumerate(authorized_changes):

                if not isinstance(change, dict):
                    raise ValueError(
                        f"Change {index} is not a valid object."
                    )

                table = change.get("table")
                record_id = change.get("record_id")
                field = change.get("field")
                old_value = change.get("old_value")
                proposed_value = change.get("proposed_value")

                # ------------------------------------------------
                # Defense-in-depth allowlists
                # ------------------------------------------------

                if table not in ALLOWED_TABLES:
                    raise ValueError(
                        f"Unauthorized table: {table}"
                    )

                if field not in ALLOWED_FIELDS.get(
                    table,
                    set(),
                ):
                    raise ValueError(
                        f"Unauthorized field: {field}"
                    )

                # ------------------------------------------------
                # Current-value verification
                # ------------------------------------------------

                select_query = text(
                    f"""
                    SELECT {field}
                    FROM {table}
                    WHERE stop_id = :record_id
                    """
                )

                row = connection.execute(
                    select_query,
                    {"record_id": record_id},
                ).mappings().first()

                if row is None:
                    raise ValueError(
                        f"Record '{record_id}' was not found."
                    )

                current_value = row[field]

                if current_value != old_value:
                    raise ValueError(
                        f"Current database value does not match "
                        f"authorized old_value for "
                        f"{table}.{field} record {record_id}. "
                        f"Expected {old_value}, found {current_value}."
                    )

                # ------------------------------------------------
                # Execute UPDATE
                # ------------------------------------------------

                update_query = text(
                    f"""
                    UPDATE {table}
                    SET {field} = :proposed_value
                    WHERE stop_id = :record_id
                      AND {field} = :old_value
                    """
                )

                result = connection.execute(
                    update_query,
                    {
                        "record_id": record_id,
                        "old_value": old_value,
                        "proposed_value": proposed_value,
                    },
                )

                if result.rowcount != 1:
                    raise ValueError(
                        f"Expected exactly one row to be updated, "
                        f"but updated {result.rowcount} rows."
                    )

                # ------------------------------------------------
                # Verify updated value
                # ------------------------------------------------

                verification = connection.execute(
                    select_query,
                    {"record_id": record_id},
                ).mappings().first()

                if verification is None:
                    raise ValueError(
                        "Updated record could not be verified."
                    )

                verified_value = verification[field]

                if verified_value != proposed_value:
                    raise ValueError(
                        f"Post-update verification failed. "
                        f"Expected {proposed_value}, "
                        f"found {verified_value}."
                    )

                executed_changes.append(
                    {
                        "table": table,
                        "record_id": record_id,
                        "field": field,
                        "old_value": old_value,
                        "new_value": verified_value,
                    }
                )

        # --------------------------------------------------------
        # Transaction committed successfully
        # --------------------------------------------------------

        return {
            "transaction_status": "COMMITTED",
            "reason": (
                "Authorized database changes were successfully "
                "applied and verified."
            ),
            "executed_changes": executed_changes,
            "admin_id": authorization_result.get(
                "admin_id"
            ),
            "timestamp": authorization_result.get(
                "timestamp"
            ),
        }

    except Exception as error:

        # SQLAlchemy's context manager automatically rolls back
        # when an exception escapes the transaction block.

        return {
            "transaction_status": "ROLLED_BACK",
            "reason": str(error),
            "executed_changes": [],
            "admin_id": authorization_result.get(
                "admin_id"
            ),
            "timestamp": authorization_result.get(
                "timestamp"
            ),
        }