from app.notifications.channels.in_app_channel import InAppChannel


def test_in_app_channel_sends_successfully() -> None:
    assert InAppChannel().send({"notification_id": "N1"})["status"] == "SENT"
