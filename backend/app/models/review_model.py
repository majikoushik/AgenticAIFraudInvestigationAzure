from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class HumanReviewModel:
    case_id: str
    decision: str
    ai_recommendation: str | None
    human_decision: str
    reviewed_by: str
    reviewer_role: str
    reason_code: str
    human_override: bool
    override_reason: str | None
    override_comparison_status: str
    override_detected_at: datetime | None
    override_detected_by: str | None
