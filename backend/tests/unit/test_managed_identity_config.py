from app.security.managed_identity_config import ManagedIdentityConfig


def test_managed_identity_summary() -> None:
    config = ManagedIdentityConfig(use_managed_identity=True, azure_client_id="client-id")
    summary = config.safe_summary()
    assert summary["use_managed_identity"] is True
    assert summary["user_assigned_identity_configured"] is True
