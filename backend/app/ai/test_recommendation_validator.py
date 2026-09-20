import json

from backend.app.ai.recommendation_validator import validate_recommendation


validation_report = {
    "dataset": "DTMS_TEST",
    "validation_status": "FAIL",
    "issue_count": 2,
    "issues": [
        {
            "rule_id": "R011",
            "severity": "HIGH",
            "issue_type": "GEOGRAPHIC",
            "description": "Invalid latitude values detected.",
            "details": {
                "affected_records": 1
            }
        },
        {
            "rule_id": "R013",
            "severity": "MEDIUM",
            "issue_type": "GEOGRAPHIC",
            "description": "Stops contain coordinates outside the configured Delhi-NCR review range.",
            "details": {
                "min_lat": 28.20808181741647,
                "max_lat": 999.0,
                "min_lon": 76.60075639009779,
                "max_lon": 77.43117
            }
        }
    ],
    "quality_observations": {
        "trip_headsign_missing": 65322,
        "direction_id_missing": 65322,
        "block_id_missing": 65322,
        "total_trips": 65322
    }
}


recommendation = {
    "issue_summary": "The dataset DTMS_TEST has failed validation due to geographic issues and missing trip attributes.",
    "primary_issue": "Invalid latitude values detected in the dataset.",
    "related_issues": [
        "Stops contain coordinates outside the configured Delhi-NCR review range."
    ],
    "evidence": [
        "Invalid latitude values detected.",
        "Stops contain coordinates outside the configured Delhi-NCR review range with min_lat: 28.20808181741647, max_lat: 999.0, min_lon: 76.60075639009779, max_lon: 77.43117."
    ],
    "unknowns": [],
    "recommended_action": "Investigate and correct the invalid latitude values and ensure all stops are within the configured Delhi-NCR review range. Obtain reliable evidence for any necessary coordinate adjustments before making changes.",
    "risk_level": "HIGH",
    "confidence": 0.0,
    "proposed_changes": [],
    "requires_admin_approval": True
}


result = validate_recommendation(
    recommendation,
    validation_report,
)

print("=== RECOMMENDATION VALIDATION ===")
print(json.dumps(result, indent=2))
