from fastapi import APIRouter

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
def get_metrics_summary() -> MetricsSummaryResponse:
    return metrics_service.get_summary_metrics()


@router.get("/case-status", response_model=CaseStatusMetrics)
def get_case_status_metrics() -> CaseStatusMetrics:
    return metrics_service.get_case_status_metrics()


@router.get("/ai-vs-human", response_model=AiVsHumanMetricsResponse)
def get_ai_vs_human_metrics() -> AiVsHumanMetricsResponse:
    return metrics_service.get_ai_vs_human_metrics()


@router.get("/operations", response_model=OperationsMetricsResponse)
def get_operations_metrics() -> OperationsMetricsResponse:
    return metrics_service.get_operations_metrics()


@router.get("/audit", response_model=AuditMetrics)
def get_audit_metrics() -> AuditMetrics:
    return metrics_service.get_audit_metrics()


@router.get("/timeseries")
def get_timeseries_metrics() -> dict:
    return metrics_service.get_timeseries_metrics()
