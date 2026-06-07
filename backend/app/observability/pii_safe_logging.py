import copy
from typing import Any


SENSITIVE_KEY_PARTS = (
    "password",
    "secret",
    "token",
    "authorization",
    "api_key",
    "connection_string",
    "account_number",
    "mobile",
    "email",
    "customer_id",
)


def sanitize_telemetry_properties(properties: dict | None) -> dict:
    if not properties:
        return {}
    return _sanitize(copy.deepcopy(properties))


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if "prompt" in lowered:
                sanitized[key] = "[REDACTED_PROMPT]"
            elif "response" in lowered:
                sanitized[key] = "[REDACTED_RESPONSE]"
            elif any(part in lowered for part in SENSITIVE_KEY_PARTS):
                sanitized[key] = "***MASKED***"
            else:
                sanitized[key] = _sanitize(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item) for item in value[:50]]
    if isinstance(value, str):
        return value if len(value) <= 500 else f"{value[:500]}..."
    return value
