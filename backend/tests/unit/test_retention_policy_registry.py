import pytest

from app.compliance.retention_policy_registry import retention_policy_registry
from app.services.errors import ApiError


def test_retention_policy_registry_returns_default_policy() -> None:
    policy = retention_policy_registry.get_policy("FRAUD_CASE")

    assert policy["policy_id"] == "RET-FRAUD-CASE"
    assert policy["requires_approval_for_purge"] is True


def test_invalid_policy_update_fails() -> None:
    with pytest.raises(ApiError):
        retention_policy_registry.update_policy("FRAUD_CASE", {"retention_days": 1, "archive_after_days": 10}, "test")
