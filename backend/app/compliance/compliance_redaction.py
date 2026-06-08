import copy
import re
from typing import Any

SENSITIVE_KEYS = {"raw_prompt", "raw_prompts", "raw_response", "raw_model_response", "chain_of_thought", "token", "tokens", "secret", "authorization", "connection_string", "api_key", "password"}


def redact_compliance_record(record: dict, redaction_level: str = "standard") -> dict:
    redacted = copy.deepcopy(record)
    return _redact_value(redacted)


def _redact_value(value: Any):
    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            lowered = key.lower()
            if lowered in SENSITIVE_KEYS or any(token in lowered for token in ["password", "secret", "authorization", "connection_string", "api_key", "raw_prompt", "raw_response"]):
                output[key] = "[REDACTED]"
            else:
                output[key] = _redact_value(item)
        return output
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, str):
        text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]", value)
        text = re.sub(r"\b\d{10,18}\b", "[REDACTED_ACCOUNT]", text)
        text = re.sub(r"\b(?:\+?\d[\d -]{8,}\d)\b", "[REDACTED_NUMBER]", text)
        return text
    return value
