from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.constants import OverrideComparisonStatus, ReasonCode, ReviewDecision, ReviewerRole, normalize_decision


class HumanReviewRequest(BaseModel):
    decision: ReviewDecision
    comment: str = Field(..., min_length=10)
    reviewed_by: str = Field(..., min_length=1)
    reviewer_role: ReviewerRole
    reason_code: ReasonCode
    evidence_acknowledged: bool
    policy_acknowledged: bool
    override_reason: str | None = None

    @field_validator("decision", mode="before")
    @classmethod
    def normalize_review_decision(cls, value: Any) -> str:
        try:
            normalized = normalize_decision(value)
        except ValueError as exc:
            raise ValueError("Decision must be one of: APPROVE, HOLD, ESCALATE, REJECT.") from exc
        if normalized is None:
            raise ValueError("Decision is required.")
        return normalized

    @model_validator(mode="after")
    def acknowledgements_required(self) -> "HumanReviewRequest":
        if not self.evidence_acknowledged:
            raise ValueError("Evidence acknowledgement is required.")
        if not self.policy_acknowledged:
            raise ValueError("Policy acknowledgement is required.")
        return self


class HumanReviewResponse(BaseModel):
    case_id: str
    previous_status: str
    new_status: str
    decision: str
    reviewed_by: str
    reviewer_role: str
    reason_code: str
    ai_recommendation: str | None
    human_decision: str
    human_override: bool
    override_reason: str | None = None
    override_comparison_status: OverrideComparisonStatus
    override_detected_at: datetime | None = None
    override_detected_by: str | None = None
    message: str


class OverrideSummaryResponse(BaseModel):
    case_id: str
    has_override: bool
    ai_recommendation: str | None
    human_decision: str | None
    override_reason: str | None = None
    override_detected_at: datetime | None = None
    override_detected_by: str | None = None
    override_comparison_status: OverrideComparisonStatus


class ReviewOptionsResponse(BaseModel):
    reviewer_role: str
    allowed_decisions: list[str]
    reason_codes: list[str]


class CloseCaseRequest(BaseModel):
    closed_by: str = Field(..., min_length=1)
    closer_role: ReviewerRole
    comment: str = Field(..., min_length=5)


class CloseCaseResponse(BaseModel):
    case_id: str
    previous_status: str
    new_status: str
    message: str
