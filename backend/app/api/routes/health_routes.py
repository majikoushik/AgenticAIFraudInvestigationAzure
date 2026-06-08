from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.config import settings
from app.observability import telemetry_events as events
from app.observability.health_checks import run_health_checks
from app.observability.telemetry_client import get_telemetry_client
from app.schemas.health import HealthResponse
from app.security.security_health import security_health_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    get_telemetry_client().track_event(events.HEALTH_CHECK_EXECUTED, {"scope": "public"})
    return HealthResponse(status="ok", service=settings.app_name)


@router.get("/api/v1/health/details")
def health_details(_: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    details = run_health_checks()
    security = security_health_service.get_security_health()
    security["required_secrets"] = {
        key.replace("_CONNECTION_STRING", "_CONNECTION").replace("APPLICATIONINSIGHTS", "APPLICATION_INSIGHTS"): value
        for key, value in security.get("required_secrets", {}).items()
    }
    details["security"] = security
    get_telemetry_client().track_event(events.HEALTH_CHECK_EXECUTED, {"scope": "details", "status": details["status"]})
    return details
