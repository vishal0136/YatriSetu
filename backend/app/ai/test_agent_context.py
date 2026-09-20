from backend.app.ai.report_loader import load_validation_report
from backend.app.ai.context_builder import build_agent_context

report_path = "validation/reports/database_validation_test.json"

request = load_validation_report(report_path)
context = build_agent_context(request)

print("=== AGENT CONTEXT TEST ===")
print("Dataset:", context["dataset"])
print("Validation status:", context["validation_status"])
print("Issue count:", len(context["issues"]))
print("Issue classifications:", context["issue_classifications"])
print("Quality observations:", context["quality_observations"])

print("\n=== FULL CONTEXT ===")
print(context)
