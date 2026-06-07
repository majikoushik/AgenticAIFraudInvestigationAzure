from app.core.constants import ReasonCode, ReviewDecision, ReviewerRole
from app.services.errors import ApiError


ALLOWED_DECISIONS_BY_ROLE: dict[ReviewerRole, set[ReviewDecision]] = {
    ReviewerRole.FRAUD_ANALYST: {
        ReviewDecision.HOLD,
        ReviewDecision.ESCALATE,
        ReviewDecision.REJECT,
    },
    ReviewerRole.FRAUD_MANAGER: {
        ReviewDecision.APPROVE,
        ReviewDecision.HOLD,
        ReviewDecision.ESCALATE,
        ReviewDecision.REJECT,
    },
    ReviewerRole.COMPLIANCE_OFFICER: {
        ReviewDecision.ESCALATE,
        ReviewDecision.HOLD,
    },
    ReviewerRole.AUDITOR: set(),
    ReviewerRole.ADMIN: {
        ReviewDecision.APPROVE,
        ReviewDecision.HOLD,
        ReviewDecision.ESCALATE,
        ReviewDecision.REJECT,
    },
    ReviewerRole.SYSTEM: set(),
}


def assert_decision_allowed(role: ReviewerRole, decision: ReviewDecision) -> None:
    if decision not in ALLOWED_DECISIONS_BY_ROLE.get(role, set()):
        raise ApiError(
            403,
            "decision_not_allowed",
            f"Reviewer role {role.value} is not allowed to perform {decision.value}",
        )


def allowed_decisions_for_role(role: ReviewerRole) -> list[str]:
    return sorted(decision.value for decision in ALLOWED_DECISIONS_BY_ROLE.get(role, set()))


def all_reason_codes() -> list[str]:
    return [reason.value for reason in ReasonCode]
