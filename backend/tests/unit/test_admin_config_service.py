from app.admin.admin_config_repository import AdminConfigRepository
from app.admin.admin_config_service import AdminConfigService
from app.admin.config_history_service import ConfigHistoryService


def _service(tmp_path) -> AdminConfigService:
    return AdminConfigService(
        AdminConfigRepository(str(tmp_path / "admin_config.json")),
        ConfigHistoryService(str(tmp_path / "history.json")),
    )


def test_admin_config_service_returns_safe_grouped_config(tmp_path) -> None:
    response = _service(tmp_path).get_safe_config("admin")

    assert response["secret_values_redacted"] is True
    assert any(category["category"] == "RAG" for category in response["categories"])


def test_admin_config_service_batch_update_and_history(tmp_path) -> None:
    service = _service(tmp_path)

    response = service.update_config([{"key": "RAG_TOP_K", "value": 8}], "admin", "test")

    assert response["updated_count"] == 1
    assert service.get_value("RAG_TOP_K") == 8
    assert service.get_config_history(key="RAG_TOP_K")[0]["new_value"] == 8


def test_admin_config_service_reports_validation_errors(tmp_path) -> None:
    response = _service(tmp_path).update_config([{"key": "RAG_TOP_K", "value": 100}], "admin", "bad")

    assert response["updated_count"] == 0
    assert response["failed_count"] == 1


def test_admin_config_service_reset_overrides(tmp_path) -> None:
    service = _service(tmp_path)
    service.update_config([{"key": "RAG_TOP_K", "value": 8}], "admin")

    response = service.reset_to_defaults("admin")

    assert response["reset_count"] == 1
    assert service.get_value("RAG_TOP_K") == 5


def test_admin_config_health_endpoint_shape(tmp_path) -> None:
    health = _service(tmp_path).get_config_health()

    assert health["secret_values_redacted"] is True
    assert health["editable_config_count"] > 0
