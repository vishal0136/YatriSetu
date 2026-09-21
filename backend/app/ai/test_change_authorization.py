from backend.app.ai.change_authorization import (
    authorize_database_change
)


# ------------------------------------------------------------
# Simulated successful safety validation
# ------------------------------------------------------------

safety_validation = {
    "validation_status": "PASS",
    "errors": [],
    "warnings": [],
    "approved_changes": [
        {
            "table": "stops",
            "record_id": "1",
            "field": "stop_lat",
            "old_value": 999.0,
            "proposed_value": 28.71797103184126,
            "evidence_source": "YatriSet Controlled Authoritative Evidence"
        }
    ],
}


# ------------------------------------------------------------
# Simulated authorized recommendation
# ------------------------------------------------------------

recommendation = {
    "issue_summary": "Invalid latitude detected.",

    "primary_issue":
        "R011: Invalid latitude values detected.",

    "related_issues": [
        "R013: Stops contain coordinates outside "
        "the configured Delhi-NCR review range."
    ],

    "evidence": [
        {
            "stop_id": "1",
            "stop_lat": 999.0,
            "stop_lon": 77.06389993096785
        }
    ],

    "unknowns": [],

    "recommended_action":
        "Replace the invalid latitude with "
        "an explicitly authorized value.",

    "risk_level": "HIGH",

    "confidence": 0.95,

    "proposed_changes": [
        {
            "table": "stops",
            "record_id": "1",
            "field": "stop_lat",
            "old_value": 999.0,
            "proposed_value": 28.71797103184126,
            "evidence_source": "YatriSet Controlled Authoritative Evidence"
        }
    ],

    "requires_admin_approval": True,
}


# ------------------------------------------------------------
# Execute authorization
# ------------------------------------------------------------

result = authorize_database_change(
    recommendation=recommendation,
    safety_validation=safety_validation,
    admin_decision="APPROVE",
    admin_id="ADMIN_DEMO_001",
)


# ------------------------------------------------------------
# Display result
# ------------------------------------------------------------

print("=== CHANGE AUTHORIZATION TEST ===")
print(result)


