from app.notifications.notification_config import notification_config


def test_notification_config_safe_defaults_do_not_expose_secrets() -> None:
    summary = notification_config.safe_summary()

    assert summary["enabled"] is True
    assert summary["mode"] == "local"
    assert summary["secret_values_redacted"] is True
    assert "teams_webhook_url" not in summary
    assert "email_smtp_password" not in summary
