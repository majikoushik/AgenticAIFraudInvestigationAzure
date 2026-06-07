from fastapi import APIRouter, Depends, Query

from app.alerting.alert_service import AlertService
from app.alerting.simulation_service import SimulationService
from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.schemas.alert_schema import AlertListResponse, AlertResolveRequest, AlertSimulationRequest

router = APIRouter(prefix="/alerts", tags=["alerts"])
alert_service = AlertService()
simulation_service = SimulationService(alert_service)


@router.get("", response_model=AlertListResponse)
def list_alerts(
    severity: str | None = None,
    alert_type: str | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG)),
) -> AlertListResponse:
    alerts = alert_service.list_alerts(alert_type, severity, status, start_date, end_date)
    return AlertListResponse(count=len(alerts), alerts=alerts)


@router.post("/evaluate")
def evaluate_alerts(_: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return alert_service.evaluate_alerts()


@router.post("/simulate")
def simulate_alert(request: AlertSimulationRequest, _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return simulation_service.simulate_alert(request.alert_type, request.severity, request.title, request.description)


@router.get("/{alert_id}")
def get_alert(alert_id: str, _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return alert_service.get_alert(alert_id)


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: str, request: AlertResolveRequest, _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return alert_service.resolve_alert(alert_id, request.actor, request.comment)
