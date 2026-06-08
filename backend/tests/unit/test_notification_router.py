from app.notifications.notification_router import NotificationRecipientRouter


def test_notification_router_routes_case_assigned_to_user() -> None:
    recipients = NotificationRecipientRouter().resolve_recipients("CASE_ASSIGNED", {"assigned_to": "fraud_analyst_01", "assigned_to_role": "FRAUD_ANALYST"})

    assert recipients[0]["recipient_type"] == "USER"
    assert recipients[0]["recipient_id"] == "fraud_analyst_01"


def test_notification_router_routes_budget_exceeded_to_admin_role() -> None:
    recipients = NotificationRecipientRouter().resolve_recipients("BUDGET_EXCEEDED", {})

    assert recipients[0]["recipient_role"] == "ADMIN"
