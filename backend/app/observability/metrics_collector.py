from app.observability.telemetry_client import get_telemetry_client


def track_business_metric(name: str, value: float, properties: dict | None = None) -> None:
    get_telemetry_client().track_metric(name, value, properties)
