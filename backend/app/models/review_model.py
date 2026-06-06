from dataclasses import dataclass


@dataclass(frozen=True)
class HumanReviewModel:
    case_id: str
    decision: str
    reviewed_by: str
    reviewer_role: str
    reason_code: str
    human_override: bool
