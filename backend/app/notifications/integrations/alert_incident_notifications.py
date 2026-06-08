from app.notifications.notification_service import notification_service


def notify_alert_created(alert: dict) -> None:
    try:
        notification_service.notify_event("ALERT_CREATED", {
            "alert_id": alert.get("alert_id"),
            "title": alert.get("title"),
            "message": alert.get("description"),
            "priority": "HIGH" if str(alert.get("severity", "")).endswith("HIGH") else "MEDIUM",
        })
    except Exception:
        return None


def notify_incident_event(event_type: str, incident: dict) -> None:
    try:
        notification_service.notify_event(event_type, {
            "incident_id": incident.get("incident_id"),
            "alert_id": incident.get("alert_id"),
            "title": incident.get("title"),
            "message": incident.get("description"),
            "assigned_to": incident.get("assigned_to"),
            "priority": "HIGH",
        })
    except Exception:
        return None
