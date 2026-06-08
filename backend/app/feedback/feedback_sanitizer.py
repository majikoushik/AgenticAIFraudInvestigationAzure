import re
from typing import Any

SENSITIVE_KEYS = {
    "api_key",
    "token",
    "password",
    "secret",
    "connection_string",
    "authorization",
    "raw_prompt",
    "prompt",
    "raw_response",
    "chain_of_thought",
    "hidden_reasoning",
    "access_token",
    "jwt",
}

SNAPSHOT_ALLOWLIST = {
    "recommended_action",
    "confidence_level",
    "policy_references",
    "source_file",
    "chunk_id",
    "safety_flags",
    "validation_result",
    "ai_provider",
    "model_or_deployment",
    "agent_name",
    "risk_indicators",
    "human_review_required",
}


def sanitize_feedback_comment(comment: str | None) -> str | None:
    if comment is None:
        return None
    return _mask_text(comment)[:2000]


def sanitize_feedback_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return _sanitize_value(payload, metadata_mode=True)


def sanitize_ai_output_snapshot(snapshot: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        return {}
    clean: dict[str, Any] = {}
    for key, value in snapshot.items():
        normalized = key.lower()
        if normalized in SENSITIVE_KEYS:
            continue
        if key in SNAPSHOT_ALLOWLIST or normalized in SNAPSHOT_ALLOWLIST:
            clean[key] = _sanitize_value(value, metadata_mode=True)
    return clean


def _sanitize_value(value: Any, metadata_mode: bool = False) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            if str(key).lower() in SENSITIVE_KEYS:
                continue
            clean[key] = _sanitize_value(item, metadata_mode)
        return clean
    if isinstance(value, list):
        return [_sanitize_value(item, metadata_mode) for item in value[:100]]
    if isinstance(value, str):
        text = _mask_text(value)
        return text[:500] if metadata_mode else text
    return value


def _mask_text(value: str) -> str:
    value = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", "[masked-email]", value)
    value = re.sub(r"\b\d{10,16}\b", "[masked-number]", value)
    value = re.sub(r"\+?\d[\d\s().-]{8,}\d", "[masked-phone]", value)
    return value
