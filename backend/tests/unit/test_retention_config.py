from app.compliance.retention_config import retention_config


def test_retention_config_loads_safe_defaults() -> None:
    summary = retention_config.safe_summary()

    assert summary["enabled"] is True
    assert summary["purge_dry_run_default"] is True
    assert summary["policy_legally_reviewed"] is False
