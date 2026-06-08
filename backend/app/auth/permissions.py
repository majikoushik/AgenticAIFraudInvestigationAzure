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
    VIEW_OWN_QUEUE = "VIEW_OWN_QUEUE"
    VIEW_TEAM_QUEUE = "VIEW_TEAM_QUEUE"
    VIEW_UNASSIGNED_QUEUE = "VIEW_UNASSIGNED_QUEUE"
    ASSIGN_CASE = "ASSIGN_CASE"
    REASSIGN_CASE = "REASSIGN_CASE"
    RELEASE_CASE = "RELEASE_CASE"
    ACCEPT_CASE = "ACCEPT_CASE"
    TRANSFER_CASE = "TRANSFER_CASE"
    VIEW_ASSIGNMENT_HISTORY = "VIEW_ASSIGNMENT_HISTORY"
    VIEW_NOTIFICATIONS = "VIEW_NOTIFICATIONS"
    MANAGE_NOTIFICATIONS = "MANAGE_NOTIFICATIONS"
    SUBMIT_AI_FEEDBACK = "SUBMIT_AI_FEEDBACK"
    VIEW_AI_FEEDBACK = "VIEW_AI_FEEDBACK"
    MANAGE_AI_FEEDBACK = "MANAGE_AI_FEEDBACK"
    EXPORT_AI_FEEDBACK = "EXPORT_AI_FEEDBACK"


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
        Permission.VIEW_OWN_QUEUE,
        Permission.ACCEPT_CASE,
        Permission.RELEASE_CASE,
        Permission.VIEW_ASSIGNMENT_HISTORY,
        Permission.VIEW_NOTIFICATIONS,
        Permission.SUBMIT_AI_FEEDBACK,
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
        Permission.VIEW_OWN_QUEUE,
        Permission.VIEW_TEAM_QUEUE,
        Permission.VIEW_UNASSIGNED_QUEUE,
        Permission.ASSIGN_CASE,
        Permission.REASSIGN_CASE,
        Permission.RELEASE_CASE,
        Permission.ACCEPT_CASE,
        Permission.TRANSFER_CASE,
        Permission.VIEW_ASSIGNMENT_HISTORY,
        Permission.VIEW_NOTIFICATIONS,
        Permission.SUBMIT_AI_FEEDBACK,
        Permission.VIEW_AI_FEEDBACK,
        Permission.MANAGE_AI_FEEDBACK,
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
        Permission.VIEW_OWN_QUEUE,
        Permission.VIEW_TEAM_QUEUE,
        Permission.ACCEPT_CASE,
        Permission.RELEASE_CASE,
        Permission.VIEW_ASSIGNMENT_HISTORY,
        Permission.VIEW_NOTIFICATIONS,
        Permission.SUBMIT_AI_FEEDBACK,
        Permission.VIEW_AI_FEEDBACK,
        Permission.MANAGE_AI_FEEDBACK,
    },
    "AUDITOR": {
        Permission.VIEW_CASES,
        Permission.VIEW_CASE_DETAILS,
        Permission.VIEW_AUDIT,
        Permission.VIEW_METRICS,
        Permission.VIEW_TEAM_QUEUE,
        Permission.VIEW_ASSIGNMENT_HISTORY,
        Permission.VIEW_NOTIFICATIONS,
        Permission.VIEW_AI_FEEDBACK,
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
