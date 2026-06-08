from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.core.constants import AuditEventType, ReviewerRole
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.security.security_health import security_health_service
from app.services.audit_service import audit_service

router = APIRouter(prefix="/security", tags=["security"])


@router.get("/health")
def get_security_health(current_user: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    result = security_health_service.get_security_health()
    audit_service.record_event(None, AuditEventType.SECURITY_HEALTH_CHECK_EXECUTED, current_user.user_id, ReviewerRole(current_user.primary_role), metadata={"status": result["status"]})
    get_telemetry_client().track_event(telemetry_events.SECURITY_HEALTH_CHECK_EXECUTED, {"status": result["status"], "deployment_mode": result["deployment_mode"]})
    return result
