from app.alerting.alert_config import AlertingConfig


def test_alerting_config_safe_summary_excludes_secrets(monkeypatch) -> None:
    monkeypatch.setenv("TEAMS_WEBHOOK_URL", "https://example.invalid/webhook")
    monkeypatch.setenv("EMAIL_SMTP_HOST", "smtp.example.invalid")
    monkeypatch.setenv("ALERT_EMAIL_RECIPIENTS", "ops@example.invalid")

    summary = AlertingConfig().safe_summary()

    assert summary["teams_webhook_configured"] is True
    assert summary["email_configured"] is True
    assert "TEAMS_WEBHOOK_URL" not in summary
    assert "thresholds" in summary
