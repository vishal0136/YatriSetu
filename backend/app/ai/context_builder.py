from backend.app.ai.contracts import AgentRequest
from backend.app.ai.report_loader import load_validation_report
from backend.app.ai.safety_policy import classify_issues


def build_agent_context(request: AgentRequest) -> dict:
    return {
        "dataset": request.dataset,
        "validation_status": request.validation_status,
        "issues": [
            {
                "rule_id": issue.rule_id,
                "severity": issue.severity,
                "issue_type": issue.issue_type,
                "description": issue.description,
                "details": issue.details,
            }
            for issue in request.issues
        ],
        "issue_classifications": classify_issues(request.issues),
        "quality_observations": request.quality_observations,
    }


if __name__ == "__main__":
    request = load_validation_report()
    context = build_agent_context(request)

    print("Agent context built successfully.")
    print("Dataset:", context["dataset"])
    print("Validation status:", context["validation_status"])
    print("Issue count:", len(context["issues"]))
    print("Quality observations:", context["quality_observations"])
