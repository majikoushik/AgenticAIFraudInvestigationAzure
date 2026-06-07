import pytest

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, assert_permission, has_permission, validate_decision_permission
from app.services.errors import ApiError


def user(role: str) -> AuthenticatedUser:
    return AuthenticatedUser(user_id=f"{role.lower()}_01", roles=[role], primary_role=role, auth_mode="local")


def test_fraud_analyst_permissions() -> None:
    analyst = user("FRAUD_ANALYST")

    assert has_permission(analyst, Permission.VIEW_CASES)
    assert not has_permission(analyst, Permission.APPROVE_DECISION)


def test_fraud_manager_can_approve() -> None:
    validate_decision_permission(user("FRAUD_MANAGER"), "APPROVE")


def test_auditor_can_view_audit_but_not_submit_decision() -> None:
    auditor = user("AUDITOR")

    assert has_permission(auditor, Permission.VIEW_AUDIT)
    with pytest.raises(ApiError):
        assert_permission(auditor, Permission.SUBMIT_HUMAN_REVIEW)


def test_admin_has_all_permissions() -> None:
    admin = user("ADMIN")

    for permission in Permission:
        assert has_permission(admin, permission)
