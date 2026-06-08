import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.observability.correlation import get_correlation_id
from app.observability.observability_config import observability_config
from app.observability.pii_safe_logging import sanitize_telemetry_properties
from app.security.secure_config_loader import secure_config_loader

logger = logging.getLogger(__name__)


class TelemetryClient:
    def __init__(self, local_store_path: Path | None = None) -> None:
        self.config = observability_config
        self.local_store_path = local_store_path or Path(__file__).resolve().parents[3] / "data" / "synthetic" / "telemetry_events.json"
        self._applicationinsights_connection_string = secure_config_loader.get_secret("APPLICATIONINSIGHTS_CONNECTION_STRING") or self.config.applicationinsights_connection_string
        self._azure_enabled = self.config.enabled and bool(self._applicationinsights_connection_string or self.config.applicationinsights_instrumentation_key)
        if self._azure_enabled:
            self._try_configure_azure_monitor()

    def track_event(self, name: str, properties: dict | None = None, measurements: dict | None = None) -> None:
        self._emit("event", name, properties, measurements)

    def track_metric(self, name: str, value: float, properties: dict | None = None) -> None:
        self._emit("metric", name, properties, {"value": value})

    def track_exception(self, exception: Exception, properties: dict | None = None) -> None:
        props = {"exception_type": type(exception).__name__, "exception_message": str(exception), **(properties or {})}
        self._emit("exception", type(exception).__name__, props, None)

    def track_dependency(self, name: str, dependency_type: str, target: str, duration_ms: float, success: bool, properties: dict | None = None) -> None:
        props = {"dependency_type": dependency_type, "target": target, "success": success, **(properties or {})}
        self._emit("dependency", name, props, {"duration_ms": duration_ms})

    def flush(self) -> None:
        return None

    def _emit(self, telemetry_type: str, name: str, properties: dict | None, measurements: dict | None) -> None:
        if not self.config.enabled:
            return
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "telemetry_type": telemetry_type,
            "name": name,
            "properties": sanitize_telemetry_properties({
                "service_name": self.config.service_name,
                "environment": self.config.environment,
                "correlation_id": get_correlation_id(),
                **(properties or {}),
            }),
            "measurements": measurements or {},
        }
        try:
            logger.info("telemetry", extra={"event_name": name, "telemetry": payload})
            if not self._azure_enabled:
                self._append_local(payload)
        except Exception:
            logger.exception("Telemetry emission failed.")

    def _append_local(self, payload: dict) -> None:
        try:
            self.local_store_path.parent.mkdir(parents=True, exist_ok=True)
            events = []
            if self.local_store_path.exists():
                events = json.loads(self.local_store_path.read_text(encoding="utf-8") or "[]")
            events.append(payload)
            self.local_store_path.write_text(json.dumps(events[-1000:], indent=2), encoding="utf-8")
        except Exception:
            logger.exception("Local telemetry store write failed.")

    def _try_configure_azure_monitor(self) -> None:
        try:
            from azure.monitor.opentelemetry import configure_azure_monitor

            configure_azure_monitor(connection_string=self._applicationinsights_connection_string)
        except Exception:
            logger.warning("Azure Monitor exporter unavailable; using local telemetry fallback.")
            self._azure_enabled = False


_telemetry_client: TelemetryClient | None = None


def get_telemetry_client() -> TelemetryClient:
    global _telemetry_client
    if _telemetry_client is None:
        _telemetry_client = TelemetryClient()
    return _telemetry_client
