from fastapi import APIRouter, Depends

from app.alerting.incident_service import IncidentService
from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.schemas.incident_schema import IncidentAssignRequest, IncidentCloseRequest, IncidentListResponse, IncidentStatusUpdateRequest, IncidentTimelineRequest

router = APIRouter(prefix="/incidents", tags=["incidents"])
incident_service = IncidentService()


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    severity: str | None = None,
    status: str | None = None,
    assigned_to: str | None = None,
    _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG)),
) -> IncidentListResponse:
    incidents = incident_service.list_incidents(severity, status, assigned_to)
    return IncidentListResponse(count=len(incidents), incidents=incidents)


@router.get("/{incident_id}")
def get_incident(incident_id: str, _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return incident_service.get_incident(incident_id)


@router.patch("/{incident_id}/status")
def update_incident_status(incident_id: str, request: IncidentStatusUpdateRequest, _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return incident_service.update_incident_status(incident_id, request.target_status, request.actor, request.comment)


@router.patch("/{incident_id}/assign")
def assign_incident(incident_id: str, request: IncidentAssignRequest, _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return incident_service.assign_incident(incident_id, request.assigned_to, request.actor, request.comment)


@router.post("/{incident_id}/timeline")
def add_timeline(incident_id: str, request: IncidentTimelineRequest, _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return incident_service.add_timeline_event(incident_id, request.actor, request.action, request.comment)


@router.post("/{incident_id}/close")
def close_incident(incident_id: str, request: IncidentCloseRequest, _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return incident_service.close_incident(incident_id, request.actor, request.comment)
