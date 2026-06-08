from fastapi import APIRouter, Depends, Query

from app.assignment.assignment_service import AssignmentService
from app.assignment.queue_service import QueueService
from app.assignment.sla_service import SlaService
from app.assignment.workload_service import WorkloadService
from app.admin.feature_flag_service import FeatureFlagService
from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.dependencies import get_current_user
from app.schemas.assignment_schema import (
    AssignmentMetricsResponse,
    AssignmentResponse,
    CaseAcceptRequest,
    CaseAssignmentRequest,
    CaseReassignmentRequest,
    CaseReleaseRequest,
    CaseTransferRequest,
    QueueResponse,
    WorkloadSummaryResponse,
)
from app.services.errors import ApiError

router = APIRouter(tags=["assignment"])
assignment_service = AssignmentService()
queue_service = QueueService()
workload_service = WorkloadService()
sla_service = SlaService()
feature_flags = FeatureFlagService()


def ensure_assignment_enabled() -> None:
    if not feature_flags.is_enabled("FEATURE_ENABLE_CASE_ASSIGNMENT"):
        raise ApiError(403, "feature_disabled", "Case assignment feature is disabled by admin configuration.")


def queue_filters(
    status: str | None = None,
    priority: str | None = None,
    sla_status: str | None = None,
    risk_level: str | None = None,
    assigned_team: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
) -> dict:
    return {
        "status": status,
        "priority": priority,
        "sla_status": sla_status,
        "risk_level": risk_level,
        "assigned_team": assigned_team,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }


@router.get("/queues/my", response_model=QueueResponse)
def get_my_queue(
    filters: dict = Depends(queue_filters),
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_OWN_QUEUE)),
) -> dict:
    ensure_assignment_enabled()
    return queue_service.get_my_queue(current_user.user_id, filters)


@router.get("/queues/unassigned", response_model=QueueResponse)
def get_unassigned_queue(
    filters: dict = Depends(queue_filters),
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_UNASSIGNED_QUEUE)),
) -> dict:
    del current_user
    ensure_assignment_enabled()
    return queue_service.get_unassigned_queue(filters)


@router.get("/queues/team", response_model=QueueResponse)
def get_team_queue(
    team: str | None = Query(default=None),
    filters: dict = Depends(queue_filters),
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_TEAM_QUEUE)),
) -> dict:
    del current_user
    ensure_assignment_enabled()
    return queue_service.get_team_queue(team, filters)


@router.get("/queues/escalated", response_model=QueueResponse)
def get_escalated_queue(
    filters: dict = Depends(queue_filters),
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_TEAM_QUEUE)),
) -> dict:
    del current_user
    ensure_assignment_enabled()
    return queue_service.get_escalated_queue(filters)


@router.get("/queues/sla-risk", response_model=QueueResponse)
def get_sla_risk_queue(
    filters: dict = Depends(queue_filters),
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_TEAM_QUEUE)),
) -> dict:
    del current_user
    ensure_assignment_enabled()
    return queue_service.get_sla_risk_queue(filters)


@router.post("/cases/{case_id}/assign", response_model=AssignmentResponse)
def assign_case(case_id: str, request: CaseAssignmentRequest, current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    ensure_assignment_enabled()
    return assignment_service.assign_case(CaseAssignmentRequest(**{**request.model_dump(), "case_id": case_id}), current_user)


@router.post("/cases/{case_id}/reassign", response_model=AssignmentResponse)
def reassign_case(case_id: str, request: CaseReassignmentRequest, current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    ensure_assignment_enabled()
    return assignment_service.reassign_case(case_id, request, current_user)


@router.post("/cases/{case_id}/accept", response_model=AssignmentResponse)
def accept_case(case_id: str, request: CaseAcceptRequest, current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    ensure_assignment_enabled()
    return assignment_service.accept_case(case_id, request, current_user)


@router.post("/cases/{case_id}/release", response_model=AssignmentResponse)
def release_case(case_id: str, request: CaseReleaseRequest, current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    ensure_assignment_enabled()
    return assignment_service.release_case(case_id, request, current_user)


@router.post("/cases/{case_id}/transfer", response_model=AssignmentResponse)
def transfer_case(case_id: str, request: CaseTransferRequest, current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    ensure_assignment_enabled()
    return assignment_service.transfer_case(case_id, request, current_user)


@router.get("/cases/{case_id}/assignment-history")
def get_assignment_history(
    case_id: str,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_ASSIGNMENT_HISTORY)),
) -> dict:
    ensure_assignment_enabled()
    return assignment_service.get_assignment_history(case_id, current_user)


@router.get("/assignment/workload", response_model=WorkloadSummaryResponse)
def get_workload(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_TEAM_QUEUE))) -> dict:
    del current_user
    ensure_assignment_enabled()
    return workload_service.get_workload_summary()


@router.get("/metrics/assignment", response_model=AssignmentMetricsResponse)
def get_assignment_metrics(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_METRICS))) -> dict:
    del current_user
    ensure_assignment_enabled()
    return workload_service.get_assignment_metrics()


@router.post("/assignment/sla/refresh")
def refresh_sla(current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    ensure_assignment_enabled()
    if not (current_user.is_admin() or current_user.primary_role == "FRAUD_MANAGER"):
        raise ApiError(403, "assignment_permission_denied", "Only fraud managers or admins can refresh assignment SLA status.")
    result = sla_service.refresh_all_sla_statuses()
    return {"message": "Assignment SLA statuses refreshed.", **result}
