import json
from datetime import UTC, datetime
from uuid import uuid4

from app.compliance.compliance_redaction import redact_compliance_record
from app.compliance.legal_hold_service import legal_hold_service
from app.compliance.retention_config import retention_config
from app.compliance.retention_repository import retention_repository
from app.core.constants import AuditEventType, ComplianceExportStatus, DataCategory, ReviewerRole
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.repositories.audit_repository import AuditRepository
from app.repositories.case_repository import CaseRepository
from app.services.errors import ApiError
from app.services.audit_service import audit_service


class ComplianceExportService:
    def __init__(self) -> None:
        self.store_path = retention_config.resolve_path(retention_config.compliance_export_store_path)

    def create_case_compliance_export(self, case_id: str, requested_by: str, include_options: dict) -> dict:
        now = datetime.now(UTC)
        export_id = f"COMP-{now.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
        audit_service.record_event(case_id, AuditEventType.COMPLIANCE_EXPORT_REQUESTED, requested_by, ReviewerRole.COMPLIANCE_OFFICER, metadata={"export_id": export_id})
        try:
            package = self._build_package(case_id, requested_by, include_options, export_id, now)
            output_path = retention_config.resolve_path(f"{retention_config.compliance_export_path}/{case_id}/{export_id}.json")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(package, indent=2, default=str) + "\n", encoding="utf-8")
            export = {
                "export_id": export_id,
                "case_id": case_id,
                "status": ComplianceExportStatus.COMPLETED.value,
                "requested_by": requested_by,
                "requested_at": now.isoformat(),
                "completed_at": datetime.now(UTC).isoformat(),
                "output_path": str(output_path),
                "manifest": package["manifest"],
                "error_message": None,
            }
            self._append_export(export)
            audit_service.record_event(case_id, AuditEventType.COMPLIANCE_EXPORT_COMPLETED, requested_by, ReviewerRole.COMPLIANCE_OFFICER, metadata={"export_id": export_id, "output_path": str(output_path)})
            get_telemetry_client().track_event(telemetry_events.COMPLIANCE_EXPORT_CREATED, {"case_id": case_id})
            return export
        except Exception as exc:
            export = {"export_id": export_id, "case_id": case_id, "status": ComplianceExportStatus.FAILED.value, "requested_by": requested_by, "requested_at": now.isoformat(), "completed_at": datetime.now(UTC).isoformat(), "output_path": None, "manifest": {}, "error_message": str(exc)}
            self._append_export(export)
            audit_service.record_event(case_id, AuditEventType.COMPLIANCE_EXPORT_FAILED, requested_by, ReviewerRole.COMPLIANCE_OFFICER, metadata={"export_id": export_id, "error": str(exc)})
            raise

    def get_export_status(self, export_id: str) -> dict:
        for item in self._read_store()["exports"]:
            if item["export_id"] == export_id:
                return item
        raise ApiError(404, "compliance_export_not_found", f"Compliance export {export_id} was not found.")

    def list_exports(self, case_id: str | None = None) -> list[dict]:
        exports = self._read_store()["exports"]
        return [item for item in exports if not case_id or item.get("case_id") == case_id]

    def _build_package(self, case_id: str, requested_by: str, include_options: dict, export_id: str, generated_at: datetime) -> dict:
        case = CaseRepository().get_case_by_id(case_id)
        if not case:
            raise ApiError(404, "case_not_found", f"Case {case_id} was not found.")
        included = ["case_details", "retention_metadata", "legal_holds"]
        package = {
            "manifest": {
                "export_id": export_id,
                "generated_by": requested_by,
                "generated_at": generated_at.isoformat(),
                "included_sections": included,
                "redaction_applied": include_options.get("redact_pii", retention_config.compliance_export_redact_pii),
                "source_files": ["data/synthetic/fraud_alerts.json"],
            },
            "case_details": case,
            "retention_metadata": {"data_category": DataCategory.FRAUD_CASE.value, "legal_hold_status": "ACTIVE" if legal_hold_service.get_holds_for_case(case_id) else "NONE"},
            "legal_holds": legal_hold_service.get_holds_for_case(case_id),
        }
        if include_options.get("include_audit", retention_config.compliance_export_include_audit):
            package["audit_trail"] = AuditRepository().list_events_by_case_id(case_id)
            included.append("audit_trail")
            package["manifest"]["source_files"].append("data/synthetic/audit_events.json")
        if include_options.get("include_feedback", retention_config.compliance_export_include_feedback):
            package["feedback_records"] = [item for item in retention_repository.list_records_by_category(DataCategory.FEEDBACK_RECORD.value) if item.get("case_id") == case_id]
            included.append("feedback_records")
        if include_options.get("include_ai_outputs", retention_config.compliance_export_include_ai_outputs):
            package["ai_outputs"] = {"included": False, "reason": "Raw prompts, raw model responses, and chain-of-thought are excluded by policy."}
            included.append("ai_outputs")
        if package["manifest"]["redaction_applied"]:
            package = redact_compliance_record(package)
        return package

    def _read_store(self) -> dict:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self.store_path.write_text('{"exports":[]}\n', encoding="utf-8")
        return json.loads(self.store_path.read_text(encoding="utf-8") or '{"exports":[]}')

    def _append_export(self, export: dict) -> None:
        store = self._read_store()
        store["exports"].append(export)
        self.store_path.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")


compliance_export_service = ComplianceExportService()
