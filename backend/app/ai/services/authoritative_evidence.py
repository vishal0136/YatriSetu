import json
from pathlib import Path
from typing import Any


EVIDENCE_FILE = (
    Path(__file__).resolve().parents[4]
    / "data"
    / "authoritative"
    / "stop_corrections.json"
)


def load_authoritative_evidence() -> dict[str, Any]:
    """
    Load the controlled authoritative evidence source.
    """

    if not EVIDENCE_FILE.exists():
        raise FileNotFoundError(
            f"Authoritative evidence file not found: {EVIDENCE_FILE}"
        )

    with EVIDENCE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_authoritative_correction(
    stop_id: str,
    field: str,
    current_value: Any,
) -> dict[str, Any] | None:
    """
    Return a correction only when the evidence matches:
      1. stop_id
      2. field
      3. current database value

    This function does NOT modify the database.
    """

    evidence = load_authoritative_evidence()

    for record in evidence.get("records", []):

        if str(record.get("stop_id")) != str(stop_id):
            continue

        if record.get("field") != field:
            continue

        if record.get("current_value") != current_value:
            continue

        if record.get("evidence_status") != "VERIFIED_FOR_EXPERIMENT":
            continue

        return {
            "verified": True,
            "source_type": evidence.get("source_type"),
            "source_name": evidence.get("source_name"),
            "source_reference": evidence.get("source_reference"),
            "stop_id": str(record["stop_id"]),
            "field": record["field"],
            "current_value": record["current_value"],
            "authoritative_value": record["authoritative_value"],
            "evidence_status": record["evidence_status"],
            "reason": record.get("reason"),
        }

    return None
