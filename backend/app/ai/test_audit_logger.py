from backend.app.ai.services.audit_logger import (
    AUDIT_FILE,
    write_audit_event,
)


print("=== AUDIT LOGGER TEST ===")

event = write_audit_event(
    event_type="TEST_EVENT",
    event_data={
        "dataset": "DTMS_TEST",
        "admin_id": "ADMIN_DEMO_001",
        "action": "CONTROLLED_TEST",
        "status": "PASS",
    },
)

print("EVENT WRITTEN:")
print(event)

print("\nAUDIT FILE:")
print(AUDIT_FILE)

if not AUDIT_FILE.exists():
    raise RuntimeError(
        "Audit file was not created."
    )

content = AUDIT_FILE.read_text(
    encoding="utf-8"
)

if "TEST_EVENT" not in content:
    raise RuntimeError(
        "Audit event was not found in the audit file."
    )

print("\n=== AUDIT LOGGER TEST: PASS ===")