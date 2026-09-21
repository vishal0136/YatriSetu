from backend.app.ai.change_authorization import authorize_database_change


BASE_CHANGE = {
    "table": "stops",
    "record_id": "1",
    "field": "stop_lat",
    "old_value": 999.0,
    "proposed_value": 28.71797103184126,
    "evidence_source": "YatriSet Controlled Authoritative Evidence",
}

BASE_RECOMMENDATION = {
    "issue_summary": "Invalid latitude detected.",
    "primary_issue": "R011: Invalid latitude values detected.",
    "related_issues": [
        "R013: Stops contain coordinates outside the configured Delhi-NCR review range."
    ],
    "evidence": [],
    "unknowns": [],
    "recommended_action": "Replace the invalid latitude with the authorized value.",
    "risk_level": "HIGH",
    "confidence": 0.95,
    "proposed_changes": [BASE_CHANGE.copy()],
    "requires_admin_approval": True,
}

BASE_SAFETY_VALIDATION = {
    "validation_status": "PASS",
    "errors": [],
    "warnings": [],
    "approved_changes": [BASE_CHANGE.copy()],
}


def run_test(name, recommendation, safety_validation, admin_decision="APPROVE"):
    result = authorize_database_change(
        recommendation=recommendation,
        safety_validation=safety_validation,
        admin_decision=admin_decision,
        admin_id="ADMIN_DEMO_001",
    )

    print(f"{name} -> {result['authorization_status']}")
    print(f"Reason: {result['reason']}")
    print()


# ------------------------------------------------------------
# 1. Valid authorization
# ------------------------------------------------------------

run_test(
    "VALID CHANGE",
    BASE_RECOMMENDATION.copy(),
    BASE_SAFETY_VALIDATION.copy(),
)


# ------------------------------------------------------------
# 2. Safety validation rejected
# ------------------------------------------------------------

rejected_safety = BASE_SAFETY_VALIDATION.copy()
rejected_safety["validation_status"] = "REJECT"
rejected_safety["approved_changes"] = []

run_test(
    "SAFETY REJECTION",
    BASE_RECOMMENDATION.copy(),
    rejected_safety,
)


# ------------------------------------------------------------
# 3. Proposed value differs from approved value
# ------------------------------------------------------------

tampered_recommendation = BASE_RECOMMENDATION.copy()
tampered_recommendation["proposed_changes"] = [BASE_CHANGE.copy()]
tampered_recommendation["proposed_changes"][0]["proposed_value"] = 28.8

run_test(
    "TAMPERED PROPOSED VALUE",
    tampered_recommendation,
    BASE_SAFETY_VALIDATION.copy(),
)


# ------------------------------------------------------------
# 4. Unauthorized table
# ------------------------------------------------------------

unauthorized_table = BASE_RECOMMENDATION.copy()
unauthorized_table["proposed_changes"] = [BASE_CHANGE.copy()]
unauthorized_table["proposed_changes"][0]["table"] = "users"

run_test(
    "UNAUTHORIZED TABLE",
    unauthorized_table,
    BASE_SAFETY_VALIDATION.copy(),
)


# ------------------------------------------------------------
# 5. Unauthorized field
# ------------------------------------------------------------

unauthorized_field = BASE_RECOMMENDATION.copy()
unauthorized_field["proposed_changes"] = [BASE_CHANGE.copy()]
unauthorized_field["proposed_changes"][0]["field"] = "agency_id"

run_test(
    "UNAUTHORIZED FIELD",
    unauthorized_field,
    BASE_SAFETY_VALIDATION.copy(),
)


# ------------------------------------------------------------
# 6. Missing evidence source
# ------------------------------------------------------------

missing_evidence = BASE_RECOMMENDATION.copy()
missing_evidence["proposed_changes"] = [BASE_CHANGE.copy()]
del missing_evidence["proposed_changes"][0]["evidence_source"]

run_test(
    "MISSING EVIDENCE SOURCE",
    missing_evidence,
    BASE_SAFETY_VALIDATION.copy(),
)


# ------------------------------------------------------------
# 7. Same old and proposed value
# ------------------------------------------------------------

same_value = BASE_RECOMMENDATION.copy()
same_value["proposed_changes"] = [BASE_CHANGE.copy()]
same_value["proposed_changes"][0]["proposed_value"] = 999.0

run_test(
    "NO-OP CHANGE",
    same_value,
    BASE_SAFETY_VALIDATION.copy(),
)


# ------------------------------------------------------------
# 8. Admin does not approve
# ------------------------------------------------------------

run_test(
    "ADMIN REJECTION",
    BASE_RECOMMENDATION.copy(),
    BASE_SAFETY_VALIDATION.copy(),
    admin_decision="REJECT",
)