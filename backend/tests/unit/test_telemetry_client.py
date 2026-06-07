import json

from app.observability.telemetry_client import TelemetryClient


def test_telemetry_client_local_mode_records_sanitized_event(tmp_path) -> None:
    path = tmp_path / "telemetry_events.json"
    client = TelemetryClient(local_store_path=path)

    client.track_event("TEST_EVENT", {"api_key": "secret", "value": "ok"}, {"duration_ms": 1.0})

    events = json.loads(path.read_text(encoding="utf-8"))
    assert events[0]["name"] == "TEST_EVENT"
    assert events[0]["properties"]["api_key"] == "***MASKED***"
    assert events[0]["measurements"]["duration_ms"] == 1.0
