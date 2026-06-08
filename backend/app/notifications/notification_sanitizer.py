from copy import deepcopy
import re
from typing import Any

SECRET_KEY_PARTS = ("api_key", "token", "password", "secret", "connection_string", "webhook", "authorization", "prompt", "response", "raw_content")


def sanitize_notification_payload(payload: dict) -> dict:
    return _sanitize_value(deepcopy(payload))


def sanitize_notification_text(text: str) -> str:
    value = str(text)
    value = re.sub(r"\b\d{12,19}\b", lambda match: "*" * (len(match.group(0)) - 4) + match.group(0)[-4:], value)
    value = re.sub(r"([A-Za-z0-9._%+-]{2})[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", r"\1***\2", value)
    value = re.sub(r"\b\+?\d[\d\s().-]{8,}\d\b", "[masked-phone]", value)
    return value[:1000]


def sanitize_recipient(recipient: dict) -> dict:
    cleaned = sanitize_notification_payload(recipient)
    if cleaned.get("email"):
        cleaned["email"] = sanitize_notification_text(cleaned["email"])
    return cleaned


def _sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            lowered = str(key).lower()
            if any(part in lowered for part in SECRET_KEY_PARTS):
                continue
            clean[key] = _sanitize_value(item)
        return clean
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    if isinstance(value, str):
        return sanitize_notification_text(value)
    return value
