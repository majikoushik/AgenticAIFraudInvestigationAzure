from app.alerting import notification_service as notification_service_module
from app.alerting.json_file_store import JsonFileStore
from app.alerting.notification_channels import LocalNotificationChannel
from app.alerting.notification_service import NotificationService


def test_notification_service_skips_when_disabled() -> None:
    service = NotificationService()

    result = service.notify({"alert_id": "ALERT-1", "severity": "SEV2_MEDIUM", "title": "Test", "description": "Test"})

    assert result["status"] == "SKIPPED"


def test_notification_service_writes_local_notification_when_enabled(tmp_path) -> None:
    service = NotificationService()
    service.local_channel = LocalNotificationChannel(JsonFileStore(str(tmp_path / "notifications.json")))
    original = notification_service_module.alerting_config.notifications_enabled
    object.__setattr__(notification_service_module.alerting_config, "notifications_enabled", True)
    try:
        result = service.notify({"alert_id": "ALERT-1", "severity": "SEV1_HIGH", "title": "Test", "description": "Test"})
    finally:
        object.__setattr__(notification_service_module.alerting_config, "notifications_enabled", original)

    assert result["status"] == "SENT"
    assert result["alert_id"] == "ALERT-1"
