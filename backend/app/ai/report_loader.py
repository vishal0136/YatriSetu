import json
from pathlib import Path

from backend.app.ai.contracts import (
    AgentRequest,
    ValidationIssue,
)


REPORT_PATH = Path("validation/reports/database_validation_test.json")


def load_validation_report(report_path: Path = REPORT_PATH) -> AgentRequest:
    with open(report_path, "r", encoding="utf-8") as file:
        report = json.load(file)

    issues = [
        ValidationIssue(
            rule_id=issue["rule_id"],
            severity=issue["severity"],
            issue_type=issue["issue_type"],
            description=issue["description"],
            details=issue.get("details", {}),
        )
        for issue in report.get("issues", [])
    ]

    return AgentRequest(
        dataset=report["dataset"],
        validation_status=report["validation_status"],
        issues=issues,
        quality_observations=report.get("quality_observations", {}),
    )


if __name__ == "__main__":
    request = load_validation_report()

    print("Validation report loaded successfully.")
    print("Dataset:", request.dataset)
    print("Status:", request.validation_status)
    print("Issues:", len(request.issues))
    print("Quality observations:", request.quality_observations)
