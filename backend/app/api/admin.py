from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.ai.recommendation_validator import validate_recommendation
from backend.app.ai.change_authorization import authorize_database_change

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)

class AdminDecisionRequest(BaseModel):
    admin_id: str

PROJECT_ROOT = Path(__file__).resolve().parents[3]

VALIDATION_REPORT = (
    PROJECT_ROOT
    / "validation"
    / "reports"
    / "database_validation_test.json"
)

RECOMMENDATION_FILE = (
    PROJECT_ROOT
    / "qwen_recommendation.json"
)


@router.get("/validation/latest")
def get_latest_validation():
    if not VALIDATION_REPORT.exists():
        raise HTTPException(
            status_code=404,
            detail="Validation report not found.",
        )

    try:
        import json

        with VALIDATION_REPORT.open("r", encoding="utf-8") as file:
            report = json.load(file)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Validation report contains invalid JSON.",
        )

    return report


@router.get("/issues")
def get_validation_issues():
    if not VALIDATION_REPORT.exists():
        raise HTTPException(
            status_code=404,
            detail="Validation report not found.",
        )

    try:
        import json

        with VALIDATION_REPORT.open("r", encoding="utf-8") as file:
            report = json.load(file)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Validation report contains invalid JSON.",
        )

    issues = report.get("issues", [])

    return {
        "dataset": report.get("dataset"),
        "validation_status": report.get("validation_status"),
        "issue_count": len(issues),
        "issues": issues,
    }

@router.get("/agent/recommendation")
def get_agent_recommendation():
    if not RECOMMENDATION_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Agent recommendation not found.",
        )

    try:
        import json

        with RECOMMENDATION_FILE.open("r", encoding="utf-8") as file:
            recommendation = json.load(file)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Agent recommendation contains invalid JSON.",
        )

    return recommendation

@router.post("/agent/reject")
def reject_agent_recommendation(request: AdminDecisionRequest):
    return {
        "status": "REJECTED",
        "admin_id": request.admin_id,
        "message": "Admin rejected the proposed change. No database modification was performed.",
    }
    
@router.post("/agent/approve")
def approve_agent_recommendation(request: AdminDecisionRequest):
    if not RECOMMENDATION_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="Agent recommendation not found.",
        )

    if not VALIDATION_REPORT.exists():
        raise HTTPException(
            status_code=404,
            detail="Validation report not found.",
        )

    if request.admin_id.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="admin_id is required.",
        )

    try:
        import json

        with RECOMMENDATION_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            recommendation = json.load(file)

        with VALIDATION_REPORT.open(
            "r",
            encoding="utf-8",
        ) as file:
            validation_report = json.load(file)

    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON data: {exc}",
        )

    # ---------------------------------------------------------
    # Gate 1: Deterministic recommendation safety validation
    # ---------------------------------------------------------

    safety_validation = validate_recommendation(
        recommendation,
        validation_report,
    )

    if safety_validation.get("validation_status") != "PASS":
        return {
            "status": "BLOCKED",
            "stage": "SAFETY_VALIDATION",
            "admin_id": request.admin_id,
            "safety_validation": safety_validation,
            "message": (
                "Recommendation failed deterministic "
                "safety validation. No database change was authorized."
            ),
        }

    # ---------------------------------------------------------
    # Gate 2: Explicit administrator authorization
    # ---------------------------------------------------------

    authorization = authorize_database_change(
        recommendation=recommendation,
        safety_validation=safety_validation,
        admin_decision="APPROVE",
        admin_id=request.admin_id,
    )

    if authorization.get("authorization_status") != "AUTHORIZED":
        return {
            "status": "BLOCKED",
            "stage": "AUTHORIZATION",
            "admin_id": request.admin_id,
            "authorization": authorization,
            "message": (
                "Database change was not authorized. "
                "No SQL transaction was executed."
            ),
        }

    # ---------------------------------------------------------
    # IMPORTANT:
    # Authorization is the end of this step.
    # SQL execution comes later.
    # ---------------------------------------------------------

    return {
        "status": "AUTHORIZED",
        "stage": "AUTHORIZATION",
        "admin_id": request.admin_id,
        "safety_validation": safety_validation,
        "authorization": authorization,
        "message": (
            "Recommendation passed deterministic safety validation "
            "and received explicit administrator approval. "
            "No database transaction was executed."
        ),
    }
    

@router.post("/agent/analyze")
def analyze_current_state():
    if not VALIDATION_REPORT.exists():
        raise HTTPException(
            status_code=404,
            detail="Validation report not found.",
        )

    try:
        import json

        with VALIDATION_REPORT.open(
            "r",
            encoding="utf-8",
        ) as file:
            validation_report = json.load(file)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Validation report contains invalid JSON.",
        )

    validation_status = validation_report.get(
        "validation_status"
    )

    issues = validation_report.get(
        "issues",
        [],
    )

    # ---------------------------------------------------------
    # Current state is clean
    # ---------------------------------------------------------

    if validation_status == "PASS" and not issues:
        return {
            "status": "NO_ACTION_REQUIRED",
            "dataset": validation_report.get("dataset"),
            "validation_status": validation_status,
            "issue_count": 0,
            "message": (
                "Current validation state is clean. "
                "No administrative correction is required."
            ),
        }

    # ---------------------------------------------------------
    # Issues exist
    # ---------------------------------------------------------

    return {
        "status": "ANALYSIS_REQUIRED",
        "dataset": validation_report.get("dataset"),
        "validation_status": validation_status,
        "issue_count": len(issues),
        "issues": issues,
        "message": (
            "Validation issues were detected. "
            "AI recommendation generation is not connected "
            "to the FastAPI runtime yet."
        ),
    }