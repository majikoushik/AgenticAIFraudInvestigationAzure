from datetime import UTC, datetime
from uuid import uuid4

from app.core.constants import AuditEventType, NotificationPriority, NotificationRecipientType, NotificationStatus, ReviewerRole
from app.notifications.notification_config import notification_config
from app.notifications.notification_dispatcher import NotificationDispatcher
from app.notifications.notification_renderer import NotificationRenderer
from app.notifications.notification_repository import NotificationRepository
from app.notifications.notification_router import NotificationRecipientRouter
from app.notifications.notification_sanitizer import sanitize_notification_payload, sanitize_notification_text
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.services.audit_service import audit_service
from app.services.errors import ApiError


class NotificationService:
    def __init__(
        self,
        repository: NotificationRepository | None = None,
        dispatcher: NotificationDispatcher | None = None,
        renderer: NotificationRenderer | None = None,
        recipient_router: NotificationRecipientRouter | None = None,
    ) -> None:
        self.repository = repository or NotificationRepository()
        self.dispatcher = dispatcher or NotificationDispatcher()
        self.renderer = renderer or NotificationRenderer()
        self.recipient_router = recipient_router or NotificationRecipientRouter()

    def create_notification(
        self,
        event_type: str,
        recipient_type: str,
        recipient_id: str | None,
        title: str | None = None,
        message: str | None = None,
        priority: str | None = None,
        channels: list[str] | None = None,
        case_id: str | None = None,
        alert_id: str | None = None,
        incident_id: str | None = None,
        metadata: dict | None = None,
        correlation_id: str | None = None,
        recipient_role: str | None = None,
        recipient_team: str | None = None,
    ) -> dict:
        now = datetime.now(UTC).isoformat()
        notification = {
            "notification_id": f"NOTIF-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "event_type": event_type,
            "priority": priority or NotificationPriority.INFO.value,
            "title": sanitize_notification_text(title or event_type.replace("_", " ").title()),
            "message": sanitize_notification_text(message or f"Notification event {event_type}."),
            "recipient_type": recipient_type,
            "recipient_id": recipient_id,
            "recipient_role": recipient_role,
            "recipient_team": recipient_team,
            "channels": channels or notification_config.default_channels,
            "status": NotificationStatus.PENDING.value if notification_config.enabled else NotificationStatus.SKIPPED.value,
            "read": False,
            "archived": False,
            "case_id": case_id,
            "alert_id": alert_id,
            "incident_id": incident_id,
            "correlation_id": correlation_id,
            "metadata": sanitize_notification_payload(metadata or {}),
            "delivery_records": [],
            "created_at": now,
            "sent_at": None,
            "read_at": None,
            "archived_at": None,
        }
        saved = self.repository.append_notification(notification)
        self._audit(AuditEventType.NOTIFICATION_CREATED, saved)
        if not notification_config.enabled:
            return saved
        return self.dispatch_notification(saved["notification_id"])

    def create_from_template(self, event_type: str, recipient: dict, context: dict) -> dict:
        rendered = self.renderer.render(event_type, context)
        return self.create_notification(
            event_type=event_type,
            recipient_type=recipient.get("recipient_type", NotificationRecipientType.ROLE.value),
            recipient_id=recipient.get("recipient_id"),
            recipient_role=recipient.get("recipient_role"),
            recipient_team=recipient.get("recipient_team"),
            title=rendered["title"],
            message=rendered["message"],
            priority=rendered["priority"],
            channels=rendered["channels"],
            case_id=context.get("case_id"),
            alert_id=context.get("alert_id"),
            incident_id=context.get("incident_id"),
            metadata=context,
        )

    def notify_event(self, event_type: str, context: dict) -> list[dict]:
        results = []
        for recipient in self.recipient_router.resolve_recipients(event_type, context):
            try:
                results.append(self.create_from_template(event_type, recipient, context))
            except Exception:
                continue
        return results

    def dispatch_notification(self, notification_id: str) -> dict:
        notification = self._get(notification_id)
        summary = self.dispatcher.dispatch(notification)
        updates = {
            "status": summary["status"],
            "delivery_records": summary["delivery_records"],
            "sent_at": datetime.now(UTC).isoformat() if summary["status"] == NotificationStatus.SENT.value else None,
        }
        updated = self.repository.update_notification(notification_id, updates)
        self._audit(AuditEventType.NOTIFICATION_SENT if updated["status"] == "SENT" else AuditEventType.NOTIFICATION_FAILED, updated)
        self._track(telemetry_events.NOTIFICATION_CREATED, updated)
        return updated

    def list_user_notifications(self, user_id: str, filters: dict | None = None) -> list[dict]:
        filters = filters or {}
        personal = self.repository.search_notifications(recipient_id=user_id, **filters)
        return personal

    def list_accessible_notifications(self, user_id: str, roles: list[str], team: str | None, filters: dict | None = None, limit: int = 100) -> list[dict]:
        filters = filters or {}
        all_items = self.repository.search_notifications(limit=500, **filters)
        allowed = [
            item for item in all_items
            if item.get("recipient_id") == user_id
            or item.get("recipient_role") in roles
            or (team and item.get("recipient_team") == team)
        ]
        return allowed[:limit]

    def list_role_notifications(self, role: str, filters: dict | None = None) -> list[dict]:
        return self.repository.search_notifications(recipient_role=role, **(filters or {}))

    def get_notification(self, notification_id: str) -> dict:
        return self._get(notification_id)

    def mark_as_read(self, notification_id: str, user_id: str) -> dict:
        notification = self._get(notification_id)
        if notification.get("recipient_id") not in {None, user_id}:
            raise ApiError(403, "notification_access_denied", "Notification is not available to this user.")
        updated = self.repository.update_notification(notification_id, {"read": True, "status": NotificationStatus.READ.value, "read_at": datetime.now(UTC).isoformat()})
        self._audit(AuditEventType.NOTIFICATION_READ, updated)
        return updated

    def mark_all_as_read(self, user_id: str) -> dict:
        count = 0
        for item in self.repository.search_notifications(recipient_id=user_id, read=False, limit=500):
            self.repository.update_notification(item["notification_id"], {"read": True, "status": NotificationStatus.READ.value, "read_at": datetime.now(UTC).isoformat()})
            count += 1
        return {"updated_count": count}

    def archive_notification(self, notification_id: str, user_id: str) -> dict:
        notification = self._get(notification_id)
        if notification.get("recipient_id") not in {None, user_id}:
            raise ApiError(403, "notification_access_denied", "Notification is not available to this user.")
        updated = self.repository.update_notification(notification_id, {"archived": True, "status": NotificationStatus.ARCHIVED.value, "archived_at": datetime.now(UTC).isoformat()})
        self._audit(AuditEventType.NOTIFICATION_ARCHIVED, updated)
        return updated

    def get_notification_summary(self, user_id: str) -> dict:
        items = self.repository.search_notifications(recipient_id=user_id, archived=False, limit=500)
        unread = [item for item in items if not item.get("read")]
        return {
            "user_id": user_id,
            "unread_count": len(unread),
            "critical_unread_count": len([item for item in unread if item.get("priority") == "CRITICAL"]),
            "high_unread_count": len([item for item in unread if item.get("priority") == "HIGH"]),
            "total_count": len(items),
            "latest_notification_at": items[0].get("created_at") if items else None,
        }

    def _get(self, notification_id: str) -> dict:
        notification = self.repository.get_notification_by_id(notification_id)
        if not notification:
            raise ApiError(404, "notification_not_found", f"Notification {notification_id} was not found.")
        return notification

    @staticmethod
    def _audit(event_type: AuditEventType, notification: dict) -> None:
        try:
            audit_service.record_event(None, event_type, "system", ReviewerRole.SYSTEM, metadata={
                "notification_id": notification.get("notification_id"),
                "event_type": notification.get("event_type"),
                "recipient_type": notification.get("recipient_type"),
                "recipient_id": notification.get("recipient_id"),
                "channels": notification.get("channels"),
                "status": notification.get("status"),
            })
        except Exception:
            return None

    @staticmethod
    def _track(event_name: str, notification: dict) -> None:
        try:
            get_telemetry_client().track_event(event_name, {
                "event_type": notification.get("event_type"),
                "priority": notification.get("priority"),
                "status": notification.get("status"),
                "recipient_type": notification.get("recipient_type"),
                "case_id": notification.get("case_id"),
                "alert_id": notification.get("alert_id"),
                "incident_id": notification.get("incident_id"),
            })
        except Exception:
            return None


notification_service = NotificationService()
