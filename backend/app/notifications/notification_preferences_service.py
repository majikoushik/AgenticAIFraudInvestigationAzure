from app.core.constants import NotificationEventType
from app.notifications.notification_config import notification_config
from app.notifications.notification_preference_repository import NotificationPreferenceRepository


CRITICAL_EVENTS = {
    NotificationEventType.SLA_BREACHED.value,
    NotificationEventType.PROMPT_INJECTION_DETECTED.value,
    NotificationEventType.GUARDRAIL_VIOLATION_DETECTED.value,
    NotificationEventType.BUDGET_EXCEEDED.value,
}


class NotificationPreferencesService:
    def __init__(self, repository: NotificationPreferenceRepository | None = None) -> None:
        self.repository = repository or NotificationPreferenceRepository()

    def get_preferences(self, user_id: str) -> dict:
        return self.repository.get_by_user_id(user_id) or self._default(user_id)

    def update_preferences(self, user_id: str, preferences: dict) -> dict:
        current = self.get_preferences(user_id)
        merged = {**current, **preferences, "user_id": user_id}
        return self.repository.upsert(user_id, merged)

    def get_effective_channels(self, user_id: str, event_type: str, default_channels: list[str] | None = None) -> list[str]:
        saved = self.repository.get_by_user_id(user_id)
        preferences = saved or self._default(user_id)
        if not self.is_notification_enabled(user_id, event_type):
            return []
        event_pref = preferences.get("event_preferences", {}).get(event_type, {})
        if saved is None:
            return default_channels or preferences.get("channels") or notification_config.default_channels
        return event_pref.get("channels") or preferences.get("channels") or default_channels or notification_config.default_channels

    def is_notification_enabled(self, user_id: str, event_type: str) -> bool:
        preferences = self.get_preferences(user_id)
        if event_type in CRITICAL_EVENTS:
            return True
        if preferences.get("enabled") is False:
            return False
        event_pref = preferences.get("event_preferences", {}).get(event_type, {})
        return event_pref.get("enabled", True)

    @staticmethod
    def _default(user_id: str) -> dict:
        return {
            "user_id": user_id,
            "role": None,
            "team": None,
            "enabled": True,
            "channels": notification_config.default_channels,
            "event_preferences": {},
            "quiet_hours": {"enabled": False, "start": "22:00", "end": "07:00", "timezone": "Asia/Kolkata"},
            "updated_at": None,
        }
