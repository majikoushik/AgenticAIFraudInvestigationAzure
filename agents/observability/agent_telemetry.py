from typing import Any


def _client():
    try:
        from app.observability.telemetry_client import get_telemetry_client

        return get_telemetry_client()
    except Exception:
        return None


def track_agent_event(name: str, properties: dict[str, Any] | None = None, measurements: dict[str, float] | None = None) -> None:
    client = _client()
    if client:
        client.track_event(name, properties, measurements)
