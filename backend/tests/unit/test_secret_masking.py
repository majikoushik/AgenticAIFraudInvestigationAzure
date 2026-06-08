from app.admin.secret_masking import is_secret_key, mask_secret_value, sanitize_config_item


def test_secret_keys_are_detected_and_masked() -> None:
    assert is_secret_key("AZURE_OPENAI_API_KEY")
    assert mask_secret_value("secret") == "[REDACTED]"


def test_secret_values_are_not_returned() -> None:
    item = sanitize_config_item({"key": "SOME_TOKEN", "value": "abc", "default_value": "def", "secret": False})

    assert item["secret"] is True
    assert item["value"] == "[REDACTED]"
    assert item["default_value"] == "[REDACTED]"
