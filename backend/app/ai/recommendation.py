from backend.app.ai.contracts import AgentRecommendation


def create_safe_recommendation(
    action: str,
    reasoning: str,
    risk_level: str = "HIGH",
    confidence: float = 0.0,
    proposed_changes: list[dict] | None = None,
) -> AgentRecommendation:

    if proposed_changes is None:
        proposed_changes = []

    confidence = max(0.0, min(1.0, confidence))

    return AgentRecommendation(
        action=action,
        confidence=confidence,
        risk_level=risk_level,
        reasoning=reasoning,
        proposed_changes=proposed_changes,
        requires_admin_approval=True,
    )
