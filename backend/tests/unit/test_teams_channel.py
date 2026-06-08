from app.notifications.channels.teams_channel import TeamsChannel


def test_teams_channel_skips_when_webhook_missing() -> None:
    assert TeamsChannel().send({"notification_id": "N1"})["status"] == "SKIPPED"
