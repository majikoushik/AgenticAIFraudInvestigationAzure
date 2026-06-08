from app.admin.admin_config_repository import AdminConfigRepository
from app.admin.admin_config_service import AdminConfigService
from app.admin.config_history_service import ConfigHistoryService
from app.admin.feature_flag_service import FeatureFlagService


def test_feature_flags_list_and_update(tmp_path) -> None:
    config = AdminConfigService(AdminConfigRepository(str(tmp_path / "admin_config.json")), ConfigHistoryService(str(tmp_path / "history.json")))
    service = FeatureFlagService(config)

    flags = service.list_feature_flags()
    updated = service.update_feature_flag("FEATURE_ENABLE_COST_DASHBOARD", False, "admin", "test")

    assert any(flag["key"] == "FEATURE_ENABLE_COST_DASHBOARD" for flag in flags)
    assert updated["value"] is False
    assert config.get_config_history(key="FEATURE_ENABLE_COST_DASHBOARD")
