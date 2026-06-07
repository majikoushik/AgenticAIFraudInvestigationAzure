from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.config import settings
from app.observability import telemetry_events as events
from app.observability.health_checks import run_health_checks
from app.observability.telemetry_client import get_telemetry_client
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    get_telemetry_client().track_event(events.HEALTH_CHECK_EXECUTED, {"scope": "public"})
    return HealthResponse(status="ok", service=settings.app_name)


@router.get("/api/v1/health/details")
def health_details(_: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    details = run_health_checks()
    get_telemetry_client().track_event(events.HEALTH_CHECK_EXECUTED, {"scope": "details", "status": details["status"]})
    return details
