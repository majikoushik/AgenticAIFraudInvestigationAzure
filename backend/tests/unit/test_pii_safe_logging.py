from app.observability.pii_safe_logging import sanitize_telemetry_properties


def test_sanitize_telemetry_properties_masks_sensitive_values() -> None:
    sanitized = sanitize_telemetry_properties(
        {
            "api_key": "secret",
            "authorization": "Bearer token",
            "email": "user@example.com",
            "nested": {"prompt": "raw prompt", "long": "x" * 700},
        }
    )

    assert sanitized["api_key"] == "***MASKED***"
    assert sanitized["authorization"] == "***MASKED***"
    assert sanitized["email"] == "***MASKED***"
    assert sanitized["nested"]["prompt"] == "[REDACTED_PROMPT]"
    assert len(sanitized["nested"]["long"]) <= 503
