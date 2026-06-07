from pathlib import Path

from app.config import settings
from app.observability.observability_config import observability_config


def run_health_checks() -> dict:
    data_path = Path(settings.synthetic_data_path)
    if not data_path.is_absolute():
        data_path = (Path(__file__).resolve().parents[2] / settings.synthetic_data_path).resolve()
    audit_path = data_path / "audit_events.json"
    checks = {
        "data_files": "ok" if data_path.exists() else "missing",
        "audit_storage": "ok" if audit_path.exists() else "missing",
        "azure_search_config": "configured" if settings.azure_search_endpoint or settings.azure_ai_search_endpoint else "missing",
        "azure_openai_config": "configured" if settings.azure_openai_endpoint and settings.azure_openai_chat_deployment else "missing",
        "application_insights": "configured" if observability_config.application_insights_configured else "missing",
        "auth_mode": settings.auth_mode,
        "telemetry": "enabled" if observability_config.enabled else "disabled",
    }
    if checks["data_files"] == "missing" or checks["audit_storage"] == "missing":
        status = "unhealthy"
    elif "missing" in {checks["azure_search_config"], checks["azure_openai_config"], checks["application_insights"]}:
        status = "degraded"
    else:
        status = "ok"
    return {"status": status, "checks": checks, "observability": observability_config.safe_summary()}
