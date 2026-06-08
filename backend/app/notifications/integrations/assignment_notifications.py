from app.notifications.notification_service import notification_service


def notify_assignment_event(event_type: str, case: dict) -> None:
    try:
        notification_service.notify_event(event_type, {
            "case_id": case.get("case_id"),
            "assigned_to": case.get("assigned_to"),
            "assigned_to_name": case.get("assigned_to_name"),
            "assigned_to_role": case.get("assigned_to_role"),
            "assigned_team": case.get("assigned_team"),
            "assignment_priority": case.get("assignment_priority"),
            "priority": "HIGH" if case.get("assignment_priority") in {"HIGH", "CRITICAL"} else "MEDIUM",
        })
    except Exception:
        return None
