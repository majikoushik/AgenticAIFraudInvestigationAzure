from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.schemas.metrics_schema import (
    AiVsHumanMetricsResponse,
    AuditMetrics,
    CaseStatusMetrics,
    MetricsSummaryResponse,
    OperationsMetricsResponse,
)
from app.services.metrics_service import metrics_service

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummaryResponse)
def get_metrics_summary(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_METRICS))) -> MetricsSummaryResponse:
    del current_user
    return metrics_service.get_summary_metrics()


@router.get("/case-status", response_model=CaseStatusMetrics)
def get_case_status_metrics(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_METRICS))) -> CaseStatusMetrics:
    del current_user
    return metrics_service.get_case_status_metrics()


@router.get("/ai-vs-human", response_model=AiVsHumanMetricsResponse)
def get_ai_vs_human_metrics(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_METRICS))) -> AiVsHumanMetricsResponse:
    del current_user
    return metrics_service.get_ai_vs_human_metrics()


@router.get("/operations", response_model=OperationsMetricsResponse)
def get_operations_metrics(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_METRICS))) -> OperationsMetricsResponse:
    del current_user
    return metrics_service.get_operations_metrics()


@router.get("/audit", response_model=AuditMetrics)
def get_audit_metrics(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_METRICS))) -> AuditMetrics:
    del current_user
    return metrics_service.get_audit_metrics()


@router.get("/timeseries")
def get_timeseries_metrics(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_METRICS))) -> dict:
    del current_user
    return metrics_service.get_timeseries_metrics()
