from app.notifications.channels.local_channel import LocalChannel


def test_local_channel_sends_successfully() -> None:
    assert LocalChannel().send({"notification_id": "N1"})["status"] == "SENT"
