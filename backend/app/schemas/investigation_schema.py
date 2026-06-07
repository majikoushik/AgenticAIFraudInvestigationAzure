from typing import Any

from pydantic import BaseModel, Field


class InvestigationPackage(BaseModel):
    case_id: str
    final_case_status: str | None = None
    ai_provider: str = "local"
    ai_mode: str = "local_deterministic"
    agent_trace: list[dict[str, Any]]
    token_usage: dict[str, int] = Field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    token_usage_records: list[dict[str, Any]] = Field(default_factory=list)
    latency_ms: float = 0.0
    citations: list[dict[str, Any]] = Field(default_factory=list)
    safety_flags: list[str] = Field(default_factory=list)
    validation_result: dict[str, Any] = Field(default_factory=dict)
    risk_indicators: list[dict[str, Any]]
    policy_references: list[dict[str, Any]]
    similar_cases: list[dict[str, Any]]
    investigation_summary: dict[str, Any]
    reviewer_validation: dict[str, Any]
    human_review_required: bool
