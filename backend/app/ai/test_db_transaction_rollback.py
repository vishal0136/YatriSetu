from sqlalchemy import text

from backend.app.ai.services.db_transaction import (
    execute_authorized_change,
)
from backend.app.ai.services.db_evidence import (
    create_test_engine,
    get_stop_evidence,
)


engine = create_test_engine()


# ------------------------------------------------------------
# Current known state
# ------------------------------------------------------------

before = get_stop_evidence(
    stop_id="1",
    db_engine=engine,
)

print("=== BEFORE ROLLBACK TEST ===")
print(before)


if before is None:
    raise RuntimeError("Test stop was not found.")


expected_latitude = before["stop_lat"]


# ------------------------------------------------------------
# Authorized first change
# ------------------------------------------------------------

authorization_result = {
    "authorization_status": "AUTHORIZED",
    "admin_id": "ADMIN_DEMO_001",
    "timestamp": "2026-09-21T00:00:00+00:00",
    "authorized_changes": [
        {
            "table": "stops",
            "record_id": "1",
            "field": "stop_lat",
            "old_value": expected_latitude,
            "proposed_value": 28.71797103184126,
            "evidence_source": (
                "YatriSet Controlled Authoritative Evidence"
            ),
        }
    ],
}


# ------------------------------------------------------------
# Deliberately force a failure AFTER an update
# ------------------------------------------------------------

try:

    with engine.begin() as connection:

        # First operation succeeds.
        update_query = text("""
            UPDATE stops
            SET stop_lat = :new_value
            WHERE stop_id = :stop_id
              AND stop_lat = :old_value
        """)

        result = connection.execute(
            update_query,
            {
                "new_value": 28.71797103184126,
                "stop_id": "1",
                "old_value": expected_latitude,
            },
        )

        if result.rowcount != 1:
            raise RuntimeError(
                "First update did not affect exactly one row."
            )

        print("\nFIRST UPDATE: SUCCESS")

        # ----------------------------------------------------
        # Deliberate failure.
        #
        # This table does not exist.
        # PostgreSQL should raise an exception and the
        # transaction should roll back.
        # ----------------------------------------------------

        connection.execute(
            text("""
                UPDATE deliberately_nonexistent_table
                SET invalid_column = 1
            """)
        )


except Exception as error:

    print("\nEXPECTED FAILURE:")
    print(error)


# ------------------------------------------------------------
# Verify rollback
# ------------------------------------------------------------

after = get_stop_evidence(
    stop_id="1",
    db_engine=engine,
)

print("\n=== AFTER ROLLBACK TEST ===")
print(after)


if after is None:
    raise RuntimeError(
        "Test stop disappeared after rollback."
    )


if after["stop_lat"] != expected_latitude:
    raise RuntimeError(
        "ROLLBACK FAILED: database retained the partial update."
    )


print("\n=== ROLLBACK TEST: PASS ===")
print(
    "The failed transaction did not retain the partial update."
)