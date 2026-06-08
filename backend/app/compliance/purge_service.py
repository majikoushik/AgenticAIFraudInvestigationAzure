import json
from datetime import UTC, datetime

from app.compliance.legal_hold_service import legal_hold_service
from app.compliance.retention_config import retention_config
from app.compliance.retention_policy_registry import retention_policy_registry
from app.compliance.retention_repository import retention_repository
from app.compliance.retention_scanner import retention_scanner
from app.core.constants import AuditEventType, DataCategory, RetentionAction, ReviewerRole
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.services.audit_service import audit_service
from app.services.errors import ApiError


class PurgeService:
    def purge_candidates(self, scan_id: str, approved_by: str, dry_run: bool = True, approval_id: str | None = None, record_ids: list[str] | None = None) -> dict:
        scan = retention_scanner.get_scan(scan_id)
        candidates = [item for item in scan.get("candidates", []) if item.get("recommended_action") == RetentionAction.PURGE.value]
        if record_ids:
            candidates = [item for item in candidates if item["record_id"] in record_ids]
        return self._process(candidates, approved_by, dry_run, approval_id)

    def purge_record(self, data_category: str, record_id: str, approved_by: str, dry_run: bool = True, approval_id: str | None = None) -> dict:
        return self._process([{"data_category": data_category, "record_id": record_id, "case_id": None}], approved_by, dry_run, approval_id)

    def _process(self, candidates: list[dict], approved_by: str, dry_run: bool, approval_id: str | None) -> dict:
        if not dry_run and retention_config.require_approval_for_purge and not approval_id:
            raise ApiError(400, "purge_approval_required", "Non-dry-run purge requires approval_id.")
        results = []
        blocked = 0
        for item in candidates:
            category = DataCategory(item["data_category"])
            policy = retention_policy_registry.get_policy(category.value)
            if not policy.get("enabled", True) or not policy.get("allow_purge", True):
                blocked += 1
                results.append({"record_id": item["record_id"], "blocked": True, "reason": "Policy does not allow purge."})
                continue
            if category == DataCategory.AUDIT_EVENT and not policy.get("allow_purge", False):
                blocked += 1
                results.append({"record_id": item["record_id"], "blocked": True, "reason": "Audit records are protected from purge by default."})
                continue
            if legal_hold_service.is_record_under_legal_hold(category.value, item["record_id"], item.get("case_id")):
                blocked += 1
                audit_service.record_event(item.get("case_id"), AuditEventType.RETENTION_PURGE_BLOCKED_LEGAL_HOLD, approved_by, ReviewerRole.COMPLIANCE_OFFICER, metadata={"record_id": item["record_id"], "data_category": category.value, "dry_run": dry_run})
                get_telemetry_client().track_event(telemetry_events.RETENTION_PURGE_BLOCKED, {"data_category": category.value})
                results.append({"record_id": item["record_id"], "blocked": True, "reason": "Legal hold active."})
                continue
            result = retention_repository.purge_record(category.value, item["record_id"], dry_run=dry_run)
            if not dry_run:
                result["tombstone"] = self._write_tombstone(category.value, item["record_id"], approved_by, approval_id)
            results.append(result)
        audit_service.record_event(None, AuditEventType.RETENTION_PURGE_DRY_RUN if dry_run else AuditEventType.RETENTION_PURGE_EXECUTED, approved_by, ReviewerRole.COMPLIANCE_OFFICER, metadata={"candidate_count": len(candidates), "blocked_count": blocked, "dry_run": dry_run, "approval_id": approval_id})
        if not dry_run:
            get_telemetry_client().track_event(telemetry_events.RETENTION_PURGE_EXECUTED, {"processed_count": len(results), "blocked_count": blocked})
        return {"action": RetentionAction.PURGE.value, "dry_run": dry_run, "requested_by": approved_by, "processed_count": len(results), "blocked_count": blocked, "results": results}

    def _write_tombstone(self, data_category: str, record_id: str, purged_by: str, approval_id: str | None) -> str:
        path = retention_config.resolve_path(f"{retention_config.archive_store_path}/tombstones/{data_category}-{record_id}.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"record_id": record_id, "data_category": data_category, "purged_at": datetime.now(UTC).isoformat(), "purged_by": purged_by, "approval_id": approval_id, "reason": "Retention period expired"}
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return str(path)


purge_service = PurgeService()
