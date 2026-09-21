import json
from pathlib import Path

from backend.app.ai.change_authorization import (
    authorize_database_change,
)
from backend.app.ai.recommendation_validator import (
    validate_recommendation,
)
from backend.app.ai.services.audit_logger import (
    log_admin_agent_run,
)
from backend.app.ai.services.db_transaction import (
    execute_authorized_change,
)
from backend.app.ai.services.post_update_validation import (
    run_post_update_validation,
)
from backend.app.ai.services.db_evidence import (
    get_stop_evidence,
)


REPORT_PATH = Path(
    "validation/reports/database_validation_test.json"
)

RECOMMENDATION_PATH = Path(
    "qwen_recommendation.json"
)


ADMIN_ID = "ADMIN_DEMO_001"
ADMIN_DECISION = "APPROVE"


print("==============================================")
print(" YATRISETU ADMIN AGENT END-TO-END TEST")
print("==============================================")


# --------------------------------------------------------
# 1. Load validation report
# --------------------------------------------------------

with REPORT_PATH.open(
    "r",
    encoding="utf-8",
) as file:
    validation_report = json.load(file)

print("\n[1] VALIDATION REPORT")
print(
    "Dataset:",
    validation_report["dataset"],
)
print(
    "Status:",
    validation_report["validation_status"],
)
print(
    "Issues:",
    validation_report["issues"],
)


# --------------------------------------------------------
# 2. Load actual Qwen recommendation
# --------------------------------------------------------

with RECOMMENDATION_PATH.open(
    "r",
    encoding="utf-8",
) as file:
    recommendation = json.load(file)

print("\n[2] QWEN RECOMMENDATION LOADED")
print(
    json.dumps(
        recommendation,
        indent=2,
    )
)


# --------------------------------------------------------
# 3. Read current DB evidence
# --------------------------------------------------------

before_evidence = get_stop_evidence(
    stop_id="1"
)

print("\n[3] DATABASE BEFORE CHANGE")
print(before_evidence)


# --------------------------------------------------------
# 4. Deterministic safety validation
# --------------------------------------------------------

safety_validation = validate_recommendation(
    recommendation,
    validation_report,
)

print("\n[4] SAFETY VALIDATION")
print(
    json.dumps(
        safety_validation,
        indent=2,
    )
)

if (
    safety_validation.get(
        "validation_status"
    )
    != "PASS"
):
    raise RuntimeError(
        "Safety validation failed. "
        "Pipeline stopped before authorization."
    )


# --------------------------------------------------------
# 5. Explicit administrator approval
# --------------------------------------------------------

authorization_result = authorize_database_change(
    recommendation=recommendation,
    safety_validation=safety_validation,
    admin_decision=ADMIN_DECISION,
    admin_id=ADMIN_ID,
)

print("\n[5] CHANGE AUTHORIZATION")
print(
    json.dumps(
        authorization_result,
        indent=2,
    )
)

if (
    authorization_result.get(
        "authorization_status"
    )
    != "AUTHORIZED"
):
    raise RuntimeError(
        "Authorization failed. "
        "Pipeline stopped before database update."
    )


# --------------------------------------------------------
# 6. Execute authorized change
# --------------------------------------------------------

transaction_result = execute_authorized_change(
    authorization_result=authorization_result,
)

print("\n[6] DATABASE TRANSACTION")
print(
    json.dumps(
        transaction_result,
        indent=2,
    )
)

if (
    transaction_result.get(
        "transaction_status"
    )
    != "COMMITTED"
):
    raise RuntimeError(
        "Database transaction did not commit."
    )


# --------------------------------------------------------
# 7. Post-update validation
# --------------------------------------------------------

post_update_validation = (
    run_post_update_validation()
)

print("\n[7] POST-UPDATE VALIDATION")
print(
    json.dumps(
        post_update_validation,
        indent=2,
    )
)

if (
    post_update_validation.get(
        "validation_status"
    )
    != "PASS"
):
    raise RuntimeError(
        "Post-update validation failed."
    )


# --------------------------------------------------------
# 8. Read database after change
# --------------------------------------------------------

after_evidence = get_stop_evidence(
    stop_id="1"
)

print("\n[8] DATABASE AFTER CHANGE")
print(after_evidence)


# --------------------------------------------------------
# 9. Write complete audit event
# --------------------------------------------------------

audit_event = log_admin_agent_run(
    validation_report=validation_report,
    recommendation=recommendation,
    safety_validation=safety_validation,
    authorization_result=authorization_result,
    transaction_result=transaction_result,
    post_update_validation=(
        post_update_validation
    ),
)

print("\n[9] AUDIT EVENT")
print(
    json.dumps(
        audit_event,
        indent=2,
    )
)


# --------------------------------------------------------
# 10. Final result
# --------------------------------------------------------

print("\n==============================================")
print(" END-TO-END ADMIN AGENT TEST: PASS")
print("==============================================")