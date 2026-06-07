import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.observability.correlation import get_correlation_id
from app.observability.observability_config import observability_config
from app.observability.pii_safe_logging import sanitize_telemetry_properties


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service_name": observability_config.service_name,
            "environment": observability_config.environment,
            "correlation_id": get_correlation_id(),
            "event_name": getattr(record, "event_name", None),
            "message": record.getMessage(),
            "logger": record.name,
        }
        for key in ("case_id", "user_id", "actor_role"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(sanitize_telemetry_properties(payload), default=str)


def configure_logging() -> None:
    level = getattr(logging, observability_config.log_level.upper(), logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter() if observability_config.log_format.lower() == "json" else logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
