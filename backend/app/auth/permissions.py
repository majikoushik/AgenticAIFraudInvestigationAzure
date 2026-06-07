from enum import StrEnum

from fastapi import Depends

from app.auth.current_user import AuthenticatedUser
from app.core.constants import ReviewDecision
from app.services.errors import ApiError


class Permission(StrEnum):
    VIEW_CASES = "VIEW_CASES"
    VIEW_CASE_DETAILS = "VIEW_CASE_DETAILS"
    RUN_AI_INVESTIGATION = "RUN_AI_INVESTIGATION"
    SUBMIT_HUMAN_REVIEW = "SUBMIT_HUMAN_REVIEW"
    APPROVE_DECISION = "APPROVE_DECISION"
    HOLD_DECISION = "HOLD_DECISION"
    ESCALATE_DECISION = "ESCALATE_DECISION"
    REJECT_DECISION = "REJECT_DECISION"
    CLOSE_CASE = "CLOSE_CASE"
    VIEW_AUDIT = "VIEW_AUDIT"
    VIEW_METRICS = "VIEW_METRICS"
    ADMIN_CONFIG = "ADMIN_CONFIG"


PERMISSIONS_BY_ROLE: dict[str, set[Permission]] = {
    "FRAUD_ANALYST": {
        Permission.VIEW_CASES,
        Permission.VIEW_CASE_DETAILS,
        Permission.RUN_AI_INVESTIGATION,
        Permission.SUBMIT_HUMAN_REVIEW,
        Permission.HOLD_DECISION,
        Permission.ESCALATE_DECISION,
        Permission.REJECT_DECISION,
        Permission.VIEW_AUDIT,
        Permission.VIEW_METRICS,
    },
    "FRAUD_MANAGER": {
        Permission.VIEW_CASES,
        Permission.VIEW_CASE_DETAILS,
        Permission.RUN_AI_INVESTIGATION,
        Permission.SUBMIT_HUMAN_REVIEW,
        Permission.APPROVE_DECISION,
        Permission.HOLD_DECISION,
        Permission.ESCALATE_DECISION,
        Permission.REJECT_DECISION,
        Permission.CLOSE_CASE,
        Permission.VIEW_AUDIT,
        Permission.VIEW_METRICS,
    },
    "COMPLIANCE_OFFICER": {
        Permission.VIEW_CASES,
        Permission.VIEW_CASE_DETAILS,
        Permission.RUN_AI_INVESTIGATION,
        Permission.SUBMIT_HUMAN_REVIEW,
        Permission.HOLD_DECISION,
        Permission.ESCALATE_DECISION,
        Permission.CLOSE_CASE,
        Permission.VIEW_AUDIT,
        Permission.VIEW_METRICS,
    },
    "AUDITOR": {
        Permission.VIEW_CASES,
        Permission.VIEW_CASE_DETAILS,
        Permission.VIEW_AUDIT,
        Permission.VIEW_METRICS,
    },
    "ADMIN": set(Permission),
}

DECISION_PERMISSION = {
    ReviewDecision.APPROVE.value: Permission.APPROVE_DECISION,
    ReviewDecision.HOLD.value: Permission.HOLD_DECISION,
    ReviewDecision.ESCALATE.value: Permission.ESCALATE_DECISION,
    ReviewDecision.REJECT.value: Permission.REJECT_DECISION,
}


def permissions_for_user(user: AuthenticatedUser) -> list[str]:
    permissions: set[Permission] = set()
    for role in user.roles:
        permissions.update(PERMISSIONS_BY_ROLE.get(role, set()))
    return sorted(permission.value for permission in permissions)


def has_permission(user: AuthenticatedUser, permission: Permission) -> bool:
    return permission.value in permissions_for_user(user)


def assert_permission(user: AuthenticatedUser, permission: Permission) -> None:
    if not has_permission(user, permission):
        raise ApiError(403, "permission_denied", f"Permission {permission.value} is required.")


def validate_decision_permission(user: AuthenticatedUser, decision: str) -> None:
    permission = DECISION_PERMISSION.get(decision.strip().upper())
    if permission is None:
        raise ApiError(400, "invalid_decision", "Decision must be one of: APPROVE, HOLD, ESCALATE, REJECT.")
    assert_permission(user, permission)


def require_permission(permission: Permission):
    from app.dependencies import get_current_user

    def dependency(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        assert_permission(current_user, permission)
        return current_user

    return dependency
