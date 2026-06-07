from datetime import datetime
from uuid import uuid4

from app.alerting.alert_config import alerting_config
from app.alerting.incident_repository import IncidentRepository
from app.alerting.incident_status_service import IncidentStatusService
from app.alerting.runbook_registry import get_runbook_for_alert
from app.core.constants import AuditEventType, IncidentStatus, ReviewerRole
from app.observability import telemetry_events
from app.observability.pii_safe_logging import sanitize_telemetry_properties
from app.observability.telemetry_client import get_telemetry_client
from app.services.audit_service import audit_service
from app.services.errors import ApiError


class IncidentService:
    def __init__(self, repository: IncidentRepository | None = None) -> None:
        self.repository = repository or IncidentRepository()
        self.status_service = IncidentStatusService()

    def list_incidents(self, severity: str | None = None, status: str | None = None, assigned_to: str | None = None) -> list[dict]:
        return self.repository.search_incidents(severity=severity, status=status, assigned_to=assigned_to)

    def get_incident(self, incident_id: str) -> dict:
        incident = self.repository.get_incident_by_id(incident_id)
        if not incident:
            raise ApiError(404, "incident_not_found", f"Incident {incident_id} was not found.")
        return incident

    def create_incident_from_alert(self, alert: dict) -> dict:
        now = datetime.utcnow().isoformat() + "Z"
        incident = {
            "incident_id": f"INC-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "alert_id": alert["alert_id"],
            "title": alert["title"],
            "description": alert["description"],
            "severity": alert["severity"],
            "status": IncidentStatus.OPEN.value,
            "assigned_to": alerting_config.default_incident_owner,
            "created_by": "system",
            "created_at": now,
            "updated_at": now,
            "acknowledged_by": None,
            "acknowledged_at": None,
            "resolved_by": None,
            "resolved_at": None,
            "closed_by": None,
            "closed_at": None,
            "runbook": alert.get("recommended_runbook") or get_runbook_for_alert(alert["alert_type"]),
            "timeline": [{"timestamp": now, "actor": "system", "action": "INCIDENT_CREATED", "comment": "Incident created from alert."}],
            "metadata": sanitize_telemetry_properties({"alert_type": alert.get("alert_type"), "source": alert.get("source")}),
        }
        self.repository.append_incident(incident)
        audit_service.record_event(None, AuditEventType.INCIDENT_CREATED, "system", ReviewerRole.SYSTEM, metadata={"incident_id": incident["incident_id"], "alert_id": alert["alert_id"]})
        get_telemetry_client().track_event(telemetry_events.INCIDENT_CREATED if hasattr(telemetry_events, "INCIDENT_CREATED") else "INCIDENT_CREATED", {"incident_id": incident["incident_id"], "alert_id": alert["alert_id"]})
        return incident

    def update_incident_status(self, incident_id: str, target_status: str, actor: str, comment: str | None = None) -> dict:
        incident = self.get_incident(incident_id)
        self.status_service.validate_transition(incident["status"], target_status)
        now = datetime.utcnow().isoformat() + "Z"
        updates = {"status": target_status, "updated_at": now}
        if target_status == IncidentStatus.ACKNOWLEDGED.value:
            updates.update({"acknowledged_by": actor, "acknowledged_at": now})
        if target_status == IncidentStatus.RESOLVED.value:
            updates.update({"resolved_by": actor, "resolved_at": now})
        if target_status == IncidentStatus.CLOSED.value:
            updates.update({"closed_by": actor, "closed_at": now})
        timeline = [*incident.get("timeline", []), {"timestamp": now, "actor": actor, "action": f"STATUS_{target_status}", "comment": comment or f"Status changed to {target_status}."}]
        updates["timeline"] = timeline
        updated = self.repository.update_incident(incident_id, updates)
        event_type = AuditEventType.INCIDENT_CLOSED if target_status == IncidentStatus.CLOSED.value else AuditEventType.INCIDENT_STATUS_CHANGED
        audit_service.record_event(None, event_type, actor, ReviewerRole.ADMIN, metadata={"incident_id": incident_id, "target_status": target_status})
        get_telemetry_client().track_event("INCIDENT_STATUS_CHANGED", {"incident_id": incident_id, "target_status": target_status})
        return updated

    def assign_incident(self, incident_id: str, assigned_to: str, actor: str, comment: str | None = None) -> dict:
        incident = self.get_incident(incident_id)
        now = datetime.utcnow().isoformat() + "Z"
        timeline = [*incident.get("timeline", []), {"timestamp": now, "actor": actor, "action": "INCIDENT_ASSIGNED", "comment": comment or f"Assigned to {assigned_to}."}]
        updated = self.repository.update_incident(incident_id, {"assigned_to": assigned_to, "updated_at": now, "timeline": timeline})
        audit_service.record_event(None, AuditEventType.INCIDENT_ASSIGNED, actor, ReviewerRole.ADMIN, metadata={"incident_id": incident_id, "assigned_to": assigned_to})
        return updated

    def add_timeline_event(self, incident_id: str, actor: str, action: str, comment: str) -> dict:
        incident = self.get_incident(incident_id)
        now = datetime.utcnow().isoformat() + "Z"
        timeline = [*incident.get("timeline", []), {"timestamp": now, "actor": actor, "action": action, "comment": comment}]
        return self.repository.update_incident(incident_id, {"updated_at": now, "timeline": timeline})

    def close_incident(self, incident_id: str, actor: str, comment: str) -> dict:
        incident = self.get_incident(incident_id)
        if incident["status"] != IncidentStatus.RESOLVED.value:
            incident = self.update_incident_status(incident_id, IncidentStatus.RESOLVED.value, actor, "Resolving before closure.")
        return self.update_incident_status(incident["incident_id"], IncidentStatus.CLOSED.value, actor, comment)
