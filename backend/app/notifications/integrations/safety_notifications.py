from app.notifications.notification_service import notification_service


def notify_safety_event(event_type: str, context: dict) -> None:
    try:
        notification_service.notify_event(event_type, {"priority": "CRITICAL", **context})
    except Exception:
        return None
