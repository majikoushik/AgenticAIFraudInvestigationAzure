import os
from typing import Any


DEFAULT_SECRET_PARTS = ("KEY", "SECRET", "TOKEN", "PASSWORD", "CONNECTION_STRING", "WEBHOOK")


def _parts() -> tuple[str, ...]:
    configured = os.getenv("CONFIG_SECRET_KEYS_PATTERN", "")
    return tuple(part.strip().upper() for part in configured.split(",") if part.strip()) or DEFAULT_SECRET_PARTS


def is_secret_key(key: str) -> bool:
    upper = (key or "").upper()
    return any(part in upper for part in _parts())


def mask_secret_value(value: Any | None) -> str | None:
    return None if value is None else "[REDACTED]"


def sanitize_config_item(item: dict) -> dict:
    clean = dict(item)
    if clean.get("secret") or is_secret_key(clean.get("key", "")):
        clean["secret"] = True
        clean["value"] = mask_secret_value(clean.get("value"))
        clean["default_value"] = mask_secret_value(clean.get("default_value"))
    return clean


def sanitize_config_response(response: dict) -> dict:
    sanitized = dict(response)
    categories = []
    for category in sanitized.get("categories", []):
        category_copy = dict(category)
        category_copy["items"] = [sanitize_config_item(item) for item in category_copy.get("items", [])]
        categories.append(category_copy)
    sanitized["categories"] = categories
    sanitized["secret_values_redacted"] = True
    return sanitized
