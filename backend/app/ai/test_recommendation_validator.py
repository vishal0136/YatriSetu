import json
from pathlib import Path

from backend.app.ai.recommendation_validator import validate_recommendation


REPORT_PATH = Path(
    "validation/reports/database_validation_test.json"
)

RECOMMENDATION_PATH = Path(
    "qwen_recommendation.json"
)


# Load validation report
with REPORT_PATH.open("r", encoding="utf-8") as file:
    validation_report = json.load(file)


# Load actual Qwen recommendation
with RECOMMENDATION_PATH.open("r", encoding="utf-8") as file:
    recommendation = json.load(file)


# Validate Qwen recommendation
result = validate_recommendation(
    recommendation,
    validation_report,
)


print("=== ACTUAL QWEN RECOMMENDATION VALIDATION ===")
print(json.dumps(result, indent=2))