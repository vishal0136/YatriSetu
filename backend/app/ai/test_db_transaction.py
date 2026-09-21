from backend.app.ai.services.db_transaction import (
    execute_authorized_change,
)
from backend.app.ai.services.db_evidence import (
    create_test_engine,
    get_stop_evidence,
)


# ------------------------------------------------------------
# Controlled authorized change
# ------------------------------------------------------------

authorization_result = {
    "authorization_status": "AUTHORIZED",
    "admin_id": "ADMIN_DEMO_001",
    "timestamp": "2026-09-20T20:30:44+00:00",
    "authorized_changes": [
        {
            "table": "stops",
            "record_id": "1",
            "field": "stop_lat",
            "old_value": 999.0,
            "proposed_value": 28.71797103184126,
            "evidence_source": (
                "YatriSet Controlled Authoritative Evidence"
            ),
        }
    ],
}


# ------------------------------------------------------------
# Create DTMS_TEST engine
# ------------------------------------------------------------

engine = create_test_engine()


# ------------------------------------------------------------
# Verify pre-transaction state
# ------------------------------------------------------------

before = get_stop_evidence(
    stop_id="1",
    db_engine=engine,
)

print("=== BEFORE TRANSACTION ===")
print(before)


if before is None:
    raise RuntimeError(
        "Controlled test stop was not found."
    )


if before["stop_lat"] != 999.0:
    raise RuntimeError(
        f"Unexpected pre-transaction latitude: "
        f"{before['stop_lat']}"
    )


# ------------------------------------------------------------
# Execute authorized transaction
# ------------------------------------------------------------

result = execute_authorized_change(
    authorization_result=authorization_result,
    db_engine=engine,
)


print("\n=== TRANSACTION RESULT ===")
print(result)


# ------------------------------------------------------------
# Verify post-transaction state
# ------------------------------------------------------------

after = get_stop_evidence(
    stop_id="1",
    db_engine=engine,
)

print("\n=== AFTER TRANSACTION ===")
print(after)


if result["transaction_status"] != "COMMITTED":
    raise RuntimeError(
        "Transaction did not commit successfully."
    )


if after is None:
    raise RuntimeError(
        "Updated stop could not be found."
    )


if after["stop_lat"] != 28.71797103184126:
    raise RuntimeError(
        f"Post-transaction verification failed: "
        f"{after['stop_lat']}"
    )


print("\n=== CONTROLLED TRANSACTION TEST: PASS ===")
