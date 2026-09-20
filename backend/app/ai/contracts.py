from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationIssue:
    rule_id: str
    severity: str
    issue_type: str
    description: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRecommendation:
    action: str
    confidence: float
    risk_level: str
    reasoning: str
    proposed_changes: list[dict[str, Any]] = field(default_factory=list)
    requires_admin_approval: bool = True


@dataclass
class AgentRequest:
    dataset: str
    validation_status: str
    issues: list[ValidationIssue] = field(default_factory=list)
    quality_observations: dict[str, Any] = field(default_factory=dict)
