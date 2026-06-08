from app.notifications.notification_dispatcher import NotificationDispatcher
from app.notifications.notification_repository import NotificationRepository
from app.notifications.notification_service import NotificationService


def test_notification_service_creates_and_dispatches_notification(tmp_path) -> None:
    service = NotificationService(repository=NotificationRepository(tmp_path / "notifications.json"), dispatcher=NotificationDispatcher())

    result = service.create_notification(
        event_type="CASE_ASSIGNED",
        recipient_type="USER",
        recipient_id="fraud_analyst_01",
        title="Case assigned",
        message="Case case-1 assigned.",
        channels=["IN_APP"],
        metadata={"token": "secret", "case_id": "case-1"},
    )

    assert result["status"] == "SENT"
    assert result["delivery_records"][0]["channel"] == "IN_APP"
    assert "token" not in result["metadata"]


def test_notification_summary_counts_unread(tmp_path) -> None:
    service = NotificationService(repository=NotificationRepository(tmp_path / "notifications.json"), dispatcher=NotificationDispatcher())
    service.create_notification("CASE_ASSIGNED", "USER", "u1", "Title", "Message", priority="CRITICAL", channels=["IN_APP"])

    summary = service.get_notification_summary("u1")

    assert summary["unread_count"] == 1
    assert summary["critical_unread_count"] == 1
