from app.notifications.channels.webhook_channel import WebhookChannel


def test_webhook_channel_skips_when_url_missing() -> None:
    assert WebhookChannel().send({"notification_id": "N1"})["status"] == "SKIPPED"
