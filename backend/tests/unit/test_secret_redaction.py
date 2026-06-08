from app.security.secret_redaction import is_sensitive_key, redact_config_dict, redact_connection_string, redact_url_with_token


def test_sensitive_key_detection() -> None:
    for key in ["API_KEY", "clientSecret", "access_token", "CONNECTION_STRING", "webhook_url", "sas"]:
        assert is_sensitive_key(key)


def test_redact_config_dict_nested() -> None:
    clean = redact_config_dict({"safe": "value", "password": "abc", "nested": {"token": "secret"}})
    assert clean["safe"] == "value"
    assert clean["password"] == "[REDACTED]"
    assert clean["nested"]["token"] == "[REDACTED]"


def test_redact_connection_and_url_tokens() -> None:
    assert "AccountKey=[REDACTED]" in redact_connection_string("Endpoint=x;AccountKey=abc")
    assert "sig=%5BREDACTED%5D" in redact_url_with_token("https://example.test/?sig=abc")
