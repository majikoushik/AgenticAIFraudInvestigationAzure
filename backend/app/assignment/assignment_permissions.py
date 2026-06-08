from app.assignment.assignment_config import assignment_config
from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, has_permission
from app.core.constants import AssignmentStatus
from app.services.errors import ApiError


def ensure_can_view_history(user: AuthenticatedUser, case: dict) -> None:
    if user.is_admin() or has_permission(user, Permission.VIEW_TEAM_QUEUE):
        return
    if has_permission(user, Permission.VIEW_ASSIGNMENT_HISTORY) and case.get("assigned_to") == user.user_id:
        return
    raise ApiError(403, "assignment_permission_denied", "Assignment history is not available for this user.")


def ensure_can_assign(user: AuthenticatedUser, case: dict, target_user_id: str) -> None:
    if user.is_admin() or has_permission(user, Permission.ASSIGN_CASE):
        return
    if (
        has_permission(user, Permission.ACCEPT_CASE)
        and assignment_config.allow_self_assignment
        and target_user_id == user.user_id
        and not case.get("assigned_to")
        and case.get("assignment_status") in {AssignmentStatus.UNASSIGNED.value, AssignmentStatus.RELEASED.value}
    ):
        return
    raise ApiError(403, "assignment_permission_denied", "User is not allowed to assign this case.")


def ensure_can_reassign(user: AuthenticatedUser) -> None:
    if user.is_admin() or has_permission(user, Permission.REASSIGN_CASE):
        return
    raise ApiError(403, "assignment_permission_denied", "User is not allowed to reassign cases.")


def ensure_can_accept(user: AuthenticatedUser, case: dict, accepted_by: str) -> None:
    if not has_permission(user, Permission.ACCEPT_CASE):
        raise ApiError(403, "assignment_permission_denied", "User is not allowed to accept cases.")
    if accepted_by != user.user_id and not user.is_admin() and not has_permission(user, Permission.REASSIGN_CASE):
        raise ApiError(403, "assignment_permission_denied", "User cannot accept a case for another investigator.")
    assigned_to = case.get("assigned_to")
    if assigned_to and assigned_to != accepted_by and not user.is_admin() and not has_permission(user, Permission.REASSIGN_CASE):
        raise ApiError(403, "assignment_permission_denied", "Case is assigned to another investigator.")


def ensure_can_release(user: AuthenticatedUser, case: dict, released_by: str) -> None:
    if user.is_admin() or has_permission(user, Permission.REASSIGN_CASE):
        return
    if (
        has_permission(user, Permission.RELEASE_CASE)
        and assignment_config.allow_analyst_release_own_case
        and released_by == user.user_id
        and case.get("assigned_to") == user.user_id
    ):
        return
    raise ApiError(403, "assignment_permission_denied", "User is not allowed to release this case.")


def ensure_can_transfer(user: AuthenticatedUser) -> None:
    if user.is_admin() or has_permission(user, Permission.TRANSFER_CASE):
        return
    raise ApiError(403, "assignment_permission_denied", "User is not allowed to transfer cases.")
