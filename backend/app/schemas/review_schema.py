from pydantic import BaseModel, Field, model_validator

from app.core.constants import ReasonCode, ReviewDecision, ReviewerRole


class HumanReviewRequest(BaseModel):
    decision: ReviewDecision
    comment: str = Field(..., min_length=10)
    reviewed_by: str = Field(..., min_length=1)
    reviewer_role: ReviewerRole
    reason_code: ReasonCode
    evidence_acknowledged: bool
    policy_acknowledged: bool
    override_reason: str | None = None

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
    human_override: bool
    message: str


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
