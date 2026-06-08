from app.notifications.channels.email_channel import EmailChannel


def test_email_channel_skips_when_config_missing() -> None:
    assert EmailChannel().send({"notification_id": "N1"})["status"] == "SKIPPED"
