from __future__ import annotations

from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


SENSITIVE_PATTERNS = ("KEY", "SECRET", "TOKEN", "PASSWORD", "CONNECTION_STRING", "WEBHOOK", "AUTHORIZATION", "CREDENTIAL", "APIKEY", "SAS")


def is_sensitive_key(key: str) -> bool:
    normalized = key.replace("-", "_").upper()
    return any(pattern in normalized for pattern in SENSITIVE_PATTERNS)


def redact_secret_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        return "[REDACTED]" if value else ""
    if isinstance(value, dict):
        return redact_config_dict(value)
    if isinstance(value, list):
        return [redact_secret_value(item) for item in value]
    return "[REDACTED]"


def redact_config_dict(config: dict) -> dict:
    clean = {}
    for key, value in config.items():
        if is_sensitive_key(str(key)):
            clean[key] = redact_secret_value(value)
        elif isinstance(value, dict):
            clean[key] = redact_config_dict(value)
        elif isinstance(value, list):
            clean[key] = [redact_config_dict(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, str) and len(value) > 500:
            clean[key] = value[:500] + "...[TRUNCATED]"
        else:
            clean[key] = value
    return clean


def redact_connection_string(value: str) -> str:
    if not value:
        return value
    parts = []
    for segment in value.split(";"):
        if not segment:
            continue
        key = segment.split("=", 1)[0]
        parts.append(f"{key}=[REDACTED]" if is_sensitive_key(key) or key.lower() in {"accountkey", "sharedaccesskey"} else segment)
    return ";".join(parts)


def redact_url_with_token(value: str) -> str:
    if not value:
        return value
    split = urlsplit(value)
    safe_query = []
    for key, item in parse_qsl(split.query, keep_blank_values=True):
        safe_query.append((key, "[REDACTED]" if is_sensitive_key(key) or key.lower() in {"sig", "signature"} else item))
    return urlunsplit((split.scheme, split.netloc, split.path, urlencode(safe_query), split.fragment))
