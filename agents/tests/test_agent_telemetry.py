from agents.observability.agent_telemetry import track_agent_event


def test_agent_telemetry_records_event_without_error() -> None:
    track_agent_event("AGENT_EXECUTION_COMPLETED", {"agent_name": "TestAgent"}, {"duration_ms": 1.0})
