from app.notifications.notification_service import notification_service


def notify_review_event(event_type: str, context: dict) -> None:
    try:
        notification_service.notify_event(event_type, context)
    except Exception:
        return None
