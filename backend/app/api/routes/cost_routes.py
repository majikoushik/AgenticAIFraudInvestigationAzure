from fastapi import APIRouter, Depends, Query, Response

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.admin.feature_flag_service import FeatureFlagService
from app.cost.azure_cost_management_client import AzureCostManagementClient
from app.cost.budget_service import BudgetService
from app.cost.cost_anomaly_detector import CostAnomalyDetector
from app.cost.cost_config import cost_monitoring_config
from app.cost.cost_export_service import CostExportService
from app.cost.cost_service import CostService
from app.schemas.cost_schema import AgentCostBreakdownResponse, BudgetStatusResponse, CaseCostBreakdownResponse, CostAnomalyResponse, CostSummaryResponse, DailyCostTrendResponse, ModelCostBreakdownResponse, TokenUsageSummaryResponse
from app.services.errors import ApiError

router = APIRouter(prefix="/cost", tags=["cost"])
cost_service = CostService()
budget_service = BudgetService(cost_service.repository)
anomaly_detector = CostAnomalyDetector(cost_service.repository)
azure_cost_client = AzureCostManagementClient()
export_service = CostExportService(cost_service)
feature_flags = FeatureFlagService()


def _require_cost_view(_: AuthenticatedUser = Depends(require_permission(Permission.VIEW_METRICS))) -> None:
    if not feature_flags.is_enabled("FEATURE_ENABLE_COST_DASHBOARD"):
        raise ApiError(403, "feature_disabled", "Cost dashboard feature is disabled by admin configuration.")
    return None


@router.get("/health")
def cost_health(_: None = Depends(_require_cost_view)) -> dict:
    return {
        "cost_monitoring_enabled": cost_monitoring_config.enabled,
        "mode": cost_monitoring_config.mode,
        "pricing_configured": cost_monitoring_config.safe_summary()["pricing_configured"],
        "azure_cost_management_enabled": azure_cost_client.is_enabled(),
        "currency": cost_monitoring_config.currency,
    }


@router.get("/summary", response_model=CostSummaryResponse)
def cost_summary(_: None = Depends(_require_cost_view)) -> dict:
    return cost_service.get_cost_summary()


@router.get("/token-usage", response_model=TokenUsageSummaryResponse)
def token_usage(case_id: str | None = None, agent_name: str | None = None, model_or_deployment: str | None = None, start_date: str | None = None, end_date: str | None = None, _: None = Depends(_require_cost_view)) -> dict:
    return cost_service.get_token_usage_summary({"case_id": case_id, "agent_name": agent_name, "model_or_deployment": model_or_deployment, "start_date": start_date, "end_date": end_date})


@router.get("/cases/{case_id}", response_model=CaseCostBreakdownResponse)
def case_cost(case_id: str, _: None = Depends(_require_cost_view)) -> dict:
    return cost_service.get_case_cost_breakdown(case_id)


@router.get("/agents", response_model=AgentCostBreakdownResponse)
def agent_costs(_: None = Depends(_require_cost_view)) -> dict:
    return cost_service.get_agent_cost_breakdown()


@router.get("/models", response_model=ModelCostBreakdownResponse)
def model_costs(_: None = Depends(_require_cost_view)) -> dict:
    return cost_service.get_model_cost_breakdown()


@router.get("/trends/daily", response_model=DailyCostTrendResponse)
def daily_trends(days: int = Query(30, ge=1, le=365), _: None = Depends(_require_cost_view)) -> dict:
    return cost_service.get_daily_cost_trend(days)


@router.get("/top-cases")
def top_cases(limit: int = Query(10, ge=1, le=100), _: None = Depends(_require_cost_view)) -> dict:
    return {"cases": cost_service.get_top_expensive_cases(limit)}


@router.get("/budget/status", response_model=BudgetStatusResponse)
def budget_status(_: None = Depends(_require_cost_view)) -> dict:
    return budget_service.get_budget_status()


@router.get("/anomalies", response_model=CostAnomalyResponse)
def anomalies(_: None = Depends(_require_cost_view)) -> dict:
    return {
        "anomalies": [
            anomaly_detector.detect_daily_cost_anomaly(),
            anomaly_detector.detect_token_usage_anomaly(),
            anomaly_detector.detect_agent_cost_anomaly(),
            anomaly_detector.detect_case_cost_anomaly(),
        ]
    }


@router.post("/recalculate")
def recalculate(_: None = Depends(_require_cost_view)) -> dict:
    return cost_service.recalculate_cost_records()


@router.get("/azure/placeholder")
def azure_placeholder(start_date: str, end_date: str, _: None = Depends(_require_cost_view)) -> dict:
    return {
        "openai": azure_cost_client.get_openai_resource_cost(start_date, end_date),
        "search": azure_cost_client.get_search_resource_cost(start_date, end_date),
        "resource_group": azure_cost_client.get_total_resource_group_cost(start_date, end_date),
    }


@router.get("/export/summary.csv")
def export_summary(_: None = Depends(_require_cost_view)) -> Response:
    return Response(content=export_service.export_cost_summary_csv(), media_type="text/csv")
