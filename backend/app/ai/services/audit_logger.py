import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[4]

AUDIT_DIR = (
    BASE_DIR
    / "validation"
    / "audit"
)

AUDIT_FILE = AUDIT_DIR / "admin_agent_audit.jsonl"


def write_audit_event(
    event_type: str,
    event_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Append one immutable-style audit event to the
    Admin Agent audit log.

    JSON Lines format is used so each event is stored
    independently and can be processed later.
    """

    AUDIT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    event = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "event_type": event_type,
        "event_data": event_data,
    }

    with AUDIT_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:

        file.write(
            json.dumps(
                event,
                ensure_ascii=False,
            )
            + "\n"
        )

    return event


def log_admin_agent_run(
    validation_report: dict[str, Any],
    recommendation: dict[str, Any],
    safety_validation: dict[str, Any],
    authorization_result: dict[str, Any],
    transaction_result: dict[str, Any],
    post_update_validation: dict[str, Any],
) -> dict[str, Any]:
    """
    Record the complete Admin Agent correction lifecycle.
    """

    return write_audit_event(
        event_type="ADMIN_AGENT_CORRECTION",
        event_data={
            "validation_report": validation_report,
            "recommendation": recommendation,
            "safety_validation": safety_validation,
            "authorization_result": authorization_result,
            "transaction_result": transaction_result,
            "post_update_validation": post_update_validation,
        },
    )