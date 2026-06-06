from app.utils.audit_sanitizer import sanitize_audit_metadata


def test_sanitizer_masks_sensitive_metadata() -> None:
    sanitized = sanitize_audit_metadata({
        "account_number": "123456789",
        "nested": {"api_key": "secret"},
        "items": [{"token": "abc"}],
    })

    assert sanitized["account_number"] == "***MASKED***"
    assert sanitized["nested"]["api_key"] == "***MASKED***"
    assert sanitized["items"][0]["token"] == "***MASKED***"


def test_sanitizer_truncates_long_values() -> None:
    sanitized = sanitize_audit_metadata({"description": "x" * 700})

    assert len(sanitized["description"]) == 503
