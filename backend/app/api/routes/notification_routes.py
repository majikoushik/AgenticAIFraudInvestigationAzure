from fastapi import APIRouter, Depends, Query

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.dependencies import get_current_user
from app.notifications.notification_config import notification_config
from app.notifications.notification_preferences_service import NotificationPreferencesService
from app.notifications.notification_repository import NotificationRepository
from app.notifications.notification_service import notification_service
from app.schemas.notification_schema import NotificationListResponse, NotificationPreference, NotificationResponse, NotificationSummaryResponse, NotificationTestRequest
from app.services.errors import ApiError

router = APIRouter(prefix="/notifications", tags=["notifications"])
admin_router = APIRouter(prefix="/admin/notifications", tags=["admin-notifications"])
preferences_service = NotificationPreferencesService()
repository = NotificationRepository()


def _filters(
    unread_only: bool | None = None,
    event_type: str | None = None,
    priority: str | None = None,
    archived: bool | None = None,
    limit: int = Query(100, ge=1, le=500),
) -> dict:
    return {
        "event_type": event_type,
        "priority": priority,
        "archived": archived,
        "read": False if unread_only else None,
        "limit": limit,
    }


@router.get("/me", response_model=NotificationListResponse)
def get_my_notifications(filters: dict = Depends(_filters), current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_NOTIFICATIONS))) -> dict:
    notifications = notification_service.list_accessible_notifications(current_user.user_id, current_user.roles, None, {key: value for key, value in filters.items() if key != "limit" and value is not None}, filters["limit"])
    return {"count": len(notifications), "notifications": notifications}


@router.get("/summary", response_model=NotificationSummaryResponse)
def get_notification_summary(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_NOTIFICATIONS))) -> dict:
    return notification_service.get_notification_summary(current_user.user_id)


@router.get("/preferences/me", response_model=NotificationPreference)
def get_my_preferences(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_NOTIFICATIONS))) -> dict:
    return preferences_service.get_preferences(current_user.user_id)


@router.patch("/preferences/me", response_model=NotificationPreference)
def update_my_preferences(payload: dict, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_NOTIFICATIONS))) -> dict:
    updated = preferences_service.update_preferences(current_user.user_id, {**payload, "role": current_user.primary_role})
    from app.core.constants import AuditEventType, ReviewerRole
    from app.services.audit_service import audit_service
    from app.observability.telemetry_client import get_telemetry_client
    from app.observability import telemetry_events

    audit_service.record_event(None, AuditEventType.NOTIFICATION_PREFERENCES_UPDATED, current_user.user_id, ReviewerRole(current_user.primary_role), metadata={"user_id": current_user.user_id})
    get_telemetry_client().track_event(telemetry_events.NOTIFICATION_PREFERENCES_UPDATED, {"user_id": current_user.user_id})
    return updated


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_NOTIFICATIONS))) -> dict:
    notification = notification_service.get_notification(notification_id)
    if not _can_access(current_user, notification):
        raise ApiError(403, "notification_access_denied", "Notification is not available to this user.")
    return notification


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_read(notification_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_NOTIFICATIONS))) -> dict:
    return notification_service.mark_as_read(notification_id, current_user.user_id)


@router.post("/read-all")
def mark_all_read(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_NOTIFICATIONS))) -> dict:
    return notification_service.mark_all_as_read(current_user.user_id)


@router.post("/{notification_id}/archive", response_model=NotificationResponse)
def archive(notification_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_NOTIFICATIONS))) -> dict:
    return notification_service.archive_notification(notification_id, current_user.user_id)


@router.post("/test", response_model=NotificationResponse)
def send_test_notification(request: NotificationTestRequest, current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    if not (current_user.is_admin() or current_user.auth_mode == "local"):
        raise ApiError(403, "notification_test_denied", "Only admins or local mode users can send test notifications.")
    result = notification_service.create_notification(
        event_type=request.event_type.value,
        recipient_type=request.recipient_type.value,
        recipient_id=request.recipient_id or current_user.user_id,
        recipient_role=request.recipient_role,
        recipient_team=request.recipient_team,
        title=request.title,
        message=request.message,
        priority=request.priority.value,
        channels=[item.value for item in request.channels] if request.channels else None,
        metadata={"test": True, "sent_by": current_user.user_id},
    )
    from app.core.constants import AuditEventType, ReviewerRole
    from app.services.audit_service import audit_service

    audit_service.record_event(None, AuditEventType.NOTIFICATION_TEST_SENT, current_user.user_id, ReviewerRole(current_user.primary_role), metadata={"notification_id": result["notification_id"]})
    return result


@admin_router.get("", response_model=NotificationListResponse)
def list_all_notifications(_: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG)), limit: int = Query(100, ge=1, le=500)) -> dict:
    notifications = repository.search_notifications(limit=limit)
    return {"count": len(notifications), "notifications": notifications}


@admin_router.get("/health")
def get_notification_health(_: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return notification_config.safe_summary()


def _can_access(user: AuthenticatedUser, notification: dict) -> bool:
    return user.is_admin() or notification.get("recipient_id") == user.user_id or notification.get("recipient_role") in user.roles
