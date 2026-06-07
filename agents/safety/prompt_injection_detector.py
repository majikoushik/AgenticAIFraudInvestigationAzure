import re

from agents.observability.llm_telemetry import track_llm_event

try:
    from app.observability import telemetry_events
except Exception:  # pragma: no cover
    telemetry_events = None


SIGNALS = [
    "ignore previous instructions",
    "disregard system prompt",
    "reveal secrets",
    "print api key",
    "bypass policy",
    "act as system",
    "delete audit logs",
    "approve without review",
]


def detect_prompt_injection(text: str) -> dict:
    lowered = text.lower()
    signals = [signal for signal in SIGNALS if signal in lowered]
    severity = "LOW"
    if len(signals) >= 2 or any(re.search(r"api key|secrets|delete audit", signal) for signal in signals):
        severity = "HIGH"
    elif signals:
        severity = "MEDIUM"
    result = {"detected": bool(signals), "signals": signals, "severity": severity}
    if result["detected"] and telemetry_events:
        track_llm_event(telemetry_events.PROMPT_INJECTION_DETECTED, {"signals": signals, "severity": severity})
    return result
