import pytest

from app.assignment.assignment_permissions import ensure_can_assign, ensure_can_release
from app.auth.current_user import AuthenticatedUser
from app.services.errors import ApiError


def user(role: str, user_id: str = "fraud_analyst_01") -> AuthenticatedUser:
    return AuthenticatedUser(user_id=user_id, roles=[role], primary_role=role, auth_mode="local")


def test_auditor_cannot_assign() -> None:
    with pytest.raises(ApiError):
        ensure_can_assign(user("AUDITOR", "auditor_01"), {"assignment_status": "UNASSIGNED", "assigned_to": None}, "fraud_analyst_01")


def test_analyst_can_self_assign_unassigned_case() -> None:
    ensure_can_assign(user("FRAUD_ANALYST"), {"assignment_status": "UNASSIGNED", "assigned_to": None}, "fraud_analyst_01")


def test_analyst_cannot_release_someone_else_case() -> None:
    with pytest.raises(ApiError):
        ensure_can_release(user("FRAUD_ANALYST"), {"assigned_to": "fraud_analyst_02"}, "fraud_analyst_01")
