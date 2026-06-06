SENSITIVE_KEY_FRAGMENTS = (
    "account_number",
    "customer_id",
    "mobile",
    "email",
    "api_key",
    "token",
    "authorization",
)


def sanitize_audit_metadata(metadata: dict) -> dict:
    return {key: _sanitize_value(key, value) for key, value in metadata.items()}


def _sanitize_value(key: str, value):
    lowered_key = key.lower()
    if any(fragment in lowered_key for fragment in SENSITIVE_KEY_FRAGMENTS):
        return "***MASKED***"

    if isinstance(value, dict):
        return sanitize_audit_metadata(value)
    if isinstance(value, list):
        return [_sanitize_value(key, item) for item in value]
    if isinstance(value, str) and len(value) > 500:
        return f"{value[:500]}..."
    return value
