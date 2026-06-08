from fastapi import APIRouter, Depends, Query

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, assert_permission, has_permission, require_permission
from app.dependencies import get_current_user
from app.feedback.feedback_analytics_service import FeedbackAnalyticsService
from app.feedback.feedback_backlog_service import FeedbackBacklogService
from app.feedback.feedback_config import feedback_config
from app.feedback.feedback_export_service import FeedbackExportService
from app.feedback.feedback_permissions import can_view_feedback
from app.feedback.feedback_service import feedback_service
from app.schemas.feedback_schema import (
    FeedbackAnalyticsResponse,
    FeedbackBacklogListResponse,
    FeedbackBacklogStatusUpdateRequest,
    FeedbackCreateRequest,
    FeedbackDispositionUpdateRequest,
    FeedbackExportResponse,
    FeedbackListResponse,
    FeedbackResponse,
)
from app.services.errors import ApiError

router = APIRouter(prefix="/feedback", tags=["ai-feedback"])
case_router = APIRouter(prefix="/cases", tags=["case-feedback"])
analytics_service = FeedbackAnalyticsService()
backlog_service = FeedbackBacklogService()
export_service = FeedbackExportService()


@router.post("", response_model=FeedbackResponse)
def submit_feedback(request: FeedbackCreateRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.SUBMIT_AI_FEEDBACK))) -> dict:
    return feedback_service.submit_feedback(request, current_user)


@router.get("/analytics/summary", response_model=FeedbackAnalyticsResponse)
def get_feedback_analytics(_: AuthenticatedUser = Depends(require_permission(Permission.VIEW_AI_FEEDBACK))) -> dict:
    return analytics_service.get_all_metrics()


@router.get("/backlog", response_model=FeedbackBacklogListResponse)
def list_backlog(_: AuthenticatedUser = Depends(require_permission(Permission.VIEW_AI_FEEDBACK)), status: str | None = None, backlog_type: str | None = None, priority: str | None = None) -> dict:
    items = backlog_service.list_backlog_items({"status": status, "backlog_type": backlog_type, "priority": priority})
    return {"count": len(items), "backlog_items": items}


@router.patch("/backlog/{backlog_id}/status")
def update_backlog_status(backlog_id: str, request: FeedbackBacklogStatusUpdateRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_AI_FEEDBACK))) -> dict:
    return backlog_service.update_backlog_status(backlog_id, request.status, request.updated_by or current_user.user_id, request.comment)


@router.post("/export/eval-dataset", response_model=FeedbackExportResponse)
def export_eval_dataset(_: AuthenticatedUser = Depends(require_permission(Permission.EXPORT_AI_FEEDBACK)), disposition_filter: str = "ACCEPTED_FOR_IMPROVEMENT") -> dict:
    return export_service.export_feedback_to_eval_dataset(disposition_filter=disposition_filter)


@router.get("/config/health")
def get_feedback_config_health(_: AuthenticatedUser = Depends(require_permission(Permission.VIEW_AI_FEEDBACK))) -> dict:
    return feedback_config.safe_summary()


@router.get("", response_model=FeedbackListResponse)
def search_feedback(
    current_user: AuthenticatedUser = Depends(get_current_user),
    case_id: str | None = None,
    target_type: str | None = None,
    rating: str | None = None,
    issue_type: str | None = None,
    severity: str | None = None,
    disposition: str | None = None,
    submitted_by: str | None = None,
    agent_name: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = Query(100, ge=1, le=500),
) -> dict:
    if not has_permission(current_user, Permission.VIEW_AI_FEEDBACK):
        assert_permission(current_user, Permission.SUBMIT_AI_FEEDBACK)
        submitted_by = current_user.user_id
    return feedback_service.search_feedback({
        "case_id": case_id,
        "target_type": target_type,
        "rating": rating,
        "issue_type": issue_type,
        "severity": severity,
        "disposition": disposition,
        "submitted_by": submitted_by,
        "agent_name": agent_name,
        "start_date": start_date,
        "end_date": end_date,
        "limit": limit,
    })


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(feedback_id: str, current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    feedback = feedback_service.get_feedback(feedback_id)
    if not can_view_feedback(current_user, feedback):
        raise ApiError(403, "feedback_access_denied", "Feedback is not available to this user.")
    return feedback


@router.patch("/{feedback_id}/disposition", response_model=FeedbackResponse)
def update_disposition(feedback_id: str, request: FeedbackDispositionUpdateRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_AI_FEEDBACK))) -> dict:
    return feedback_service.update_feedback_disposition(feedback_id, request, current_user)


@case_router.get("/{case_id}/feedback", response_model=FeedbackListResponse)
def get_case_feedback(case_id: str, current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    if not has_permission(current_user, Permission.VIEW_AI_FEEDBACK):
        assert_permission(current_user, Permission.SUBMIT_AI_FEEDBACK)
    result = feedback_service.get_case_feedback(case_id)
    if not has_permission(current_user, Permission.VIEW_AI_FEEDBACK):
        result["feedback_records"] = [item for item in result["feedback_records"] if item.get("submitted_by") == current_user.user_id]
        result["count"] = len(result["feedback_records"])
    return result
