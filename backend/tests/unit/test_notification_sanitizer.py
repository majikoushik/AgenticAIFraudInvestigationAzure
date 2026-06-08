from app.notifications.notification_sanitizer import sanitize_notification_payload, sanitize_notification_text


def test_sanitizer_removes_secret_prompt_and_response_keys() -> None:
    payload = {"api_key": "x", "token": "y", "prompt": "raw", "safe": {"password": "z", "case_id": "case-1"}}

    sanitized = sanitize_notification_payload(payload)

    assert "api_key" not in sanitized
    assert "token" not in sanitized
    assert "prompt" not in sanitized
    assert "password" not in sanitized["safe"]
    assert sanitized["safe"]["case_id"] == "case-1"


def test_sanitizer_masks_email_and_account_like_values() -> None:
    text = sanitize_notification_text("Email fraud_analyst_01@example.com account 1234567890123456")

    assert "fraud_analyst_01@example.com" not in text
    assert "************3456" in text
