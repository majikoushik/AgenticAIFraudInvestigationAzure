from app.notifications.notification_repository import NotificationRepository


def test_notification_repository_creates_file_and_sanitizes(tmp_path) -> None:
    repo = NotificationRepository(tmp_path / "notifications.json")

    saved = repo.append_notification({"notification_id": "NOTIF-1", "created_at": "2026-06-08T00:00:00Z", "metadata": {"token": "secret", "case_id": "case-1"}})

    assert (tmp_path / "notifications.json").exists()
    assert saved["metadata"]["case_id"] == "case-1"
    assert "token" not in saved["metadata"]


def test_notification_repository_search_filters_user_and_read(tmp_path) -> None:
    repo = NotificationRepository(tmp_path / "notifications.json")
    repo.append_notification({"notification_id": "N1", "recipient_id": "u1", "read": False, "created_at": "2026-06-08T00:00:00Z"})
    repo.append_notification({"notification_id": "N2", "recipient_id": "u2", "read": False, "created_at": "2026-06-08T01:00:00Z"})

    result = repo.search_notifications(recipient_id="u1", read=False)

    assert len(result) == 1
    assert result[0]["notification_id"] == "N1"
