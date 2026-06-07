from app.alerting.alert_config import alerting_config
from app.alerting.notification_channels import EmailNotificationChannel, LocalNotificationChannel, TeamsWebhookChannel
from app.core.constants import AuditEventType, ReviewerRole
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.services.audit_service import audit_service


class NotificationService:
    def __init__(self) -> None:
        self.local_channel = LocalNotificationChannel()
        self.teams_channel = TeamsWebhookChannel()
        self.email_channel = EmailNotificationChannel()

    def notify(self, alert: dict, incident: dict | None = None) -> dict:
        payload = {
            "channel": "local",
            "alert_id": alert.get("alert_id"),
            "incident_id": incident.get("incident_id") if incident else None,
            "severity": alert.get("severity"),
            "title": alert.get("title"),
            "message": alert.get("description"),
        }
        try:
            if not alerting_config.notifications_enabled:
                payload["status"] = "SKIPPED"
                payload["error_message"] = "Notifications disabled."
                return payload
            notification = self.local_channel.send(payload)
            audit_service.record_event(None, AuditEventType.NOTIFICATION_SENT, "system", ReviewerRole.SYSTEM, metadata={"alert_id": alert.get("alert_id"), "incident_id": payload["incident_id"]})
            get_telemetry_client().track_event(telemetry_events.NOTIFICATION_SENT if hasattr(telemetry_events, "NOTIFICATION_SENT") else "NOTIFICATION_SENT", {"alert_id": alert.get("alert_id")})
            return notification
        except Exception as exc:
            audit_service.record_event(None, AuditEventType.NOTIFICATION_FAILED, "system", ReviewerRole.SYSTEM, metadata={"alert_id": alert.get("alert_id"), "error_type": type(exc).__name__})
            return {**payload, "status": "FAILED", "error_message": str(exc)}
