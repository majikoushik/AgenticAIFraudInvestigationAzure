from app.notifications.notification_service import notification_service


def notify_sla_event(case: dict) -> None:
    status = case.get("sla_status")
    if status not in {"AT_RISK", "BREACHED"}:
        return
    event_type = "SLA_BREACHED" if status == "BREACHED" else "SLA_AT_RISK"
    try:
        notification_service.notify_event(event_type, {
            "case_id": case.get("case_id"),
            "assigned_to": case.get("assigned_to"),
            "assigned_to_role": case.get("assigned_to_role"),
            "assigned_team": case.get("assigned_team"),
            "sla_due_at": case.get("sla_due_at"),
            "priority": "CRITICAL" if status == "BREACHED" else "HIGH",
        })
    except Exception:
        return None
