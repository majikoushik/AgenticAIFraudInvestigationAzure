from app.notifications.notification_preference_repository import NotificationPreferenceRepository
from app.notifications.notification_preferences_service import NotificationPreferencesService


def test_preferences_default_to_default_channels(tmp_path) -> None:
    service = NotificationPreferencesService(NotificationPreferenceRepository(tmp_path / "prefs.json"))

    assert service.get_effective_channels("u1", "CASE_ASSIGNED", ["IN_APP"]) == ["IN_APP"]


def test_user_can_update_preferences(tmp_path) -> None:
    service = NotificationPreferencesService(NotificationPreferenceRepository(tmp_path / "prefs.json"))

    updated = service.update_preferences("u1", {"enabled": False, "channels": ["LOCAL"]})

    assert updated["enabled"] is False
    assert service.is_notification_enabled("u1", "CASE_ASSIGNED") is False
