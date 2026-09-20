from backend.app.ai.contracts import ValidationIssue


AUTO_RECOMMENDABLE_RULES = {
    "R011",  # Invalid latitude
    "R012",  # Invalid longitude
    "R014",  # Invalid stop sequence
    "R015",  # Invalid arrival/departure value
    "R016",  # Departure before arrival
    "R017",  # Invalid service date range
}


HIGH_RISK_RULES = {
    "R001",
    "R002",
    "R004",
    "R005",
    "R006",
    "R007",
    "R008",
    "R009",
    "R010",
    "R019",
    "R020",
    "R023",
}


def classify_issue(issue: ValidationIssue) -> str:
    if issue.rule_id in HIGH_RISK_RULES:
        return "REQUIRES_ADMIN_REVIEW"

    if issue.rule_id in AUTO_RECOMMENDABLE_RULES:
        return "AI_RECOMMENDATION_ALLOWED"

    return "OBSERVATION_ONLY"


def classify_issues(issues: list[ValidationIssue]) -> list[dict]:
    return [
        {
            "rule_id": issue.rule_id,
            "classification": classify_issue(issue),
        }
        for issue in issues
    ]
