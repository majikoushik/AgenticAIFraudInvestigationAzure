from datetime import datetime, timedelta
from uuid import uuid4

from app.alerting.alert_config import alerting_config
from app.alerting.alert_evaluator import AlertEvaluator
from app.alerting.alert_repository import AlertRepository
from app.alerting.incident_service import IncidentService
from app.alerting.notification_service import NotificationService
from app.alerting.runbook_registry import get_runbook_for_alert
from app.core.constants import AlertSeverity, AuditEventType, ReviewerRole
from app.observability import telemetry_events
from app.observability.correlation import get_correlation_id
from app.observability.pii_safe_logging import sanitize_telemetry_properties
from app.observability.telemetry_client import get_telemetry_client
from app.services.audit_service import audit_service
from app.services.errors import ApiError
from app.notifications.integrations.alert_incident_notifications import notify_alert_created


class AlertService:
    def __init__(self, repository: AlertRepository | None = None, incident_service: IncidentService | None = None) -> None:
        self.repository = repository or AlertRepository()
        self.incident_service = incident_service or IncidentService()
        self.notification_service = NotificationService()
        self.evaluator = AlertEvaluator()

    def evaluate_alerts(self) -> dict:
        results = self.evaluator.evaluate_all_rules()
        alerts = [self.create_alert(result["alert"]) for result in results if result.get("alert")]
        return {"evaluated_rules": len(results), "alerts_created": len(alerts), "alerts": alerts, "results": results}

    def create_alert(self, alert_data: dict) -> dict:
        duplicate = self._active_duplicate(alert_data["alert_type"])
        if duplicate:
            return duplicate
        now = datetime.utcnow().isoformat() + "Z"
        alert = {
            "alert_id": f"ALERT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "status": "ACTIVE",
            "created_at": now,
            "resolved_at": None,
            "correlation_id": get_correlation_id(),
            "recommended_runbook": alert_data.get("recommended_runbook") or get_runbook_for_alert(alert_data["alert_type"]),
            **alert_data,
        }
        alert["properties"] = sanitize_telemetry_properties(alert.get("properties", {}))
        self.repository.append_alert(alert)
        audit_service.record_event(None, AuditEventType.ALERT_CREATED, "system", ReviewerRole.SYSTEM, metadata={"alert_id": alert["alert_id"], "alert_type": alert["alert_type"], "severity": alert["severity"]})
        get_telemetry_client().track_event(telemetry_events.ALERT_CREATED, {"alert_id": alert["alert_id"], "alert_type": alert["alert_type"], "severity": alert["severity"]})
        incident = None
        if alerting_config.incident_auto_create_enabled and alert["severity"] in {AlertSeverity.SEV0_CRITICAL.value, AlertSeverity.SEV1_HIGH.value}:
            incident = self.incident_service.create_incident_from_alert(alert)
        self.notification_service.notify(alert, incident)
        notify_alert_created(alert)
        return alert

    def list_alerts(self, alert_type: str | None = None, severity: str | None = None, status: str | None = None, start_date: str | None = None, end_date: str | None = None) -> list[dict]:
        return self.repository.search_alerts(alert_type, severity, status, start_date, end_date)

    def get_alert(self, alert_id: str) -> dict:
        alert = self.repository.get_alert_by_id(alert_id)
        if not alert:
            raise ApiError(404, "alert_not_found", f"Alert {alert_id} was not found.")
        return alert

    def resolve_alert(self, alert_id: str, actor: str, comment: str | None = None) -> dict:
        del comment
        alert = self.repository.update_alert_status(alert_id, "RESOLVED")
        audit_service.record_event(None, AuditEventType.ALERT_RESOLVED, actor, ReviewerRole.ADMIN, metadata={"alert_id": alert_id})
        get_telemetry_client().track_event(telemetry_events.ALERT_RESOLVED, {"alert_id": alert_id})
        return alert

    def create_incident_from_alert(self, alert_id: str) -> dict:
        return self.incident_service.create_incident_from_alert(self.get_alert(alert_id))

    def _active_duplicate(self, alert_type: str) -> dict | None:
        cutoff = datetime.utcnow() - timedelta(minutes=15)
        for alert in self.repository.search_alerts(alert_type=alert_type, status="ACTIVE"):
            try:
                created = datetime.fromisoformat(alert.get("created_at", "").replace("Z", "+00:00")).replace(tzinfo=None)
                if created >= cutoff:
                    return alert
            except Exception:
                continue
        return None
