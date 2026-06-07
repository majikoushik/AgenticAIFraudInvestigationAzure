from typing import Any

from agents.observability.agent_telemetry import track_agent_event


def track_business_event(name: str, properties: dict[str, Any] | None = None, measurements: dict[str, float] | None = None) -> None:
    track_agent_event(name, properties, measurements)
