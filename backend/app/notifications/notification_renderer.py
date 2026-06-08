import re

from app.notifications.notification_sanitizer import sanitize_notification_text
from app.notifications.notification_template_repository import NotificationTemplateRepository


PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


class NotificationRenderer:
    def __init__(self, repository: NotificationTemplateRepository | None = None) -> None:
        self.repository = repository or NotificationTemplateRepository()

    def render(self, event_type: str, context: dict) -> dict:
        template = self.repository.get_by_event_type(event_type)
        if not template:
            return {
                "title": sanitize_notification_text(event_type.replace("_", " ").title()),
                "message": sanitize_notification_text(context.get("message") or f"Notification event {event_type}."),
                "priority": context.get("priority") or "INFO",
                "channels": context.get("channels") or ["IN_APP", "LOCAL"],
            }
        return {
            "title": self._render_text(template["title_template"], context),
            "message": self._render_text(template["message_template"], context),
            "priority": context.get("priority") or template.get("default_priority", "INFO"),
            "channels": context.get("channels") or template.get("default_channels", ["IN_APP", "LOCAL"]),
        }

    @staticmethod
    def _render_text(template: str, context: dict) -> str:
        def replace(match):
            return str(context.get(match.group(1), ""))

        return sanitize_notification_text(PLACEHOLDER_PATTERN.sub(replace, template))
