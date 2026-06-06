from typing import Any

from pydantic import BaseModel


class InvestigationPackage(BaseModel):
    case_id: str
    final_case_status: str | None = None
    agent_trace: list[dict[str, Any]]
    risk_indicators: list[dict[str, Any]]
    policy_references: list[dict[str, Any]]
    similar_cases: list[dict[str, Any]]
    investigation_summary: dict[str, Any]
    reviewer_validation: dict[str, Any]
    human_review_required: bool
