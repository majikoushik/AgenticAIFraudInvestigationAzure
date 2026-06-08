import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.compliance.legal_hold_service import legal_hold_service
from app.compliance.retention_config import retention_config
from app.compliance.retention_policy_registry import retention_policy_registry
from app.compliance.retention_repository import SOURCE_MAP, retention_repository
from app.core.constants import AuditEventType, DataCategory, LegalHoldStatus, RetentionAction, RetentionStatus, ReviewerRole
from app.observability import telemetry_events
from app.observability.telemetry_client import get_telemetry_client
from app.services.audit_service import audit_service


class RetentionScanner:
    def __init__(self) -> None:
        self.path = retention_config.resolve_path(retention_config.scan_results_store_path)

    def scan_all(self, dry_run: bool = True) -> dict:
        return self._scan(list(SOURCE_MAP.keys()), dry_run)

    def scan_category(self, data_category: str, dry_run: bool = True) -> dict:
        return self._scan([DataCategory(data_category)], dry_run)

    def evaluate_record(self, record: dict, data_category: str, policy: dict) -> dict:
        category = DataCategory(data_category)
        record_id = retention_repository.get_record_id(record, category.value)
        case_id = retention_repository.get_case_id(record)
        created_at = retention_repository.get_record_created_at(record, category.value)
        if created_at is None:
            created_at = datetime.now(UTC)
        archive_at = created_at + timedelta(days=int(policy["archive_after_days"]))
        purge_at = created_at + timedelta(days=int(policy["purge_after_days"]))
        now = datetime.now(UTC)
        under_hold = legal_hold_service.is_record_under_legal_hold(category.value, record_id, case_id)
        days_until_purge = (purge_at - now).days
        if under_hold:
            status = RetentionStatus.LEGAL_HOLD
            action = RetentionAction.LEGAL_HOLD
            reason = "Record is under active legal hold."
            legal_status = LegalHoldStatus.ACTIVE
        elif not policy.get("enabled", True):
            status = RetentionStatus.EXEMPT
            action = RetentionAction.EXEMPT
            reason = "Retention policy is disabled."
            legal_status = LegalHoldStatus.NONE
        elif now >= purge_at:
            status = RetentionStatus.PURGE_ELIGIBLE
            action = RetentionAction.PURGE
            reason = "Record reached purge threshold."
            legal_status = LegalHoldStatus.NONE
        elif now >= archive_at:
            status = RetentionStatus.ARCHIVE_ELIGIBLE
            action = RetentionAction.ARCHIVE
            reason = "Record reached archive threshold."
            legal_status = LegalHoldStatus.NONE
        elif days_until_purge <= retention_config.review_lookahead_days:
            status = RetentionStatus.REVIEW_REQUIRED
            action = RetentionAction.REVIEW_REQUIRED
            reason = "Record is near purge eligibility and requires review."
            legal_status = LegalHoldStatus.NONE
        else:
            status = RetentionStatus.ACTIVE
            action = RetentionAction.KEEP
            reason = "Record remains within active retention window."
            legal_status = LegalHoldStatus.NONE
        metadata = {
            "data_category": category.value,
            "classification": policy["classification"],
            "created_at": created_at.isoformat(),
            "retention_policy_id": policy["policy_id"],
            "retention_status": status.value,
            "archive_eligible_at": archive_at.isoformat(),
            "purge_eligible_at": purge_at.isoformat(),
            "legal_hold_status": legal_status.value,
            "legal_hold_id": None,
            "last_retention_scan_at": now.isoformat(),
        }
        return {
            "record_id": record_id,
            "data_category": category.value,
            "classification": policy["classification"],
            "created_at": created_at.isoformat(),
            "retention_status": status.value,
            "recommended_action": action.value,
            "reason": reason,
            "legal_hold_status": legal_status.value,
            "days_until_purge": days_until_purge,
            "source_file": retention_repository.source_file_for_category(category.value),
            "case_id": case_id,
            "retention_metadata": metadata,
        }

    def get_scan(self, scan_id: str) -> dict:
        for scan in self._read_store()["scans"]:
            if scan["scan_id"] == scan_id:
                return scan
        from app.services.errors import ApiError

        raise ApiError(404, "retention_scan_not_found", f"Retention scan {scan_id} was not found.")

    def latest_candidates(self) -> list[dict]:
        scans = self._read_store()["scans"]
        if not scans:
            return []
        return scans[-1].get("candidates", [])

    def _scan(self, categories: list[DataCategory], dry_run: bool) -> dict:
        started = datetime.now(UTC)
        scan_id = f"RETSCAN-{started.strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
        audit_service.record_event(None, AuditEventType.RETENTION_SCAN_STARTED, "system", ReviewerRole.SYSTEM, metadata={"scan_id": scan_id, "dry_run": dry_run})
        get_telemetry_client().track_event(telemetry_events.RETENTION_SCAN_STARTED, {"dry_run": str(dry_run)})
        candidates = []
        records_scanned = 0
        errors = []
        for category in categories:
            try:
                policy = retention_policy_registry.get_policy(category.value)
                for record in retention_repository.list_records_by_category(category.value):
                    records_scanned += 1
                    evaluated = self.evaluate_record(record, category.value, policy)
                    if not dry_run:
                        retention_repository.update_record_retention_metadata(category.value, evaluated["record_id"], evaluated["retention_metadata"])
                    if evaluated["recommended_action"] != RetentionAction.KEEP.value:
                        candidates.append({key: value for key, value in evaluated.items() if key != "retention_metadata"})
            except Exception as exc:
                errors.append(f"{category.value}: {exc}")
        completed = datetime.now(UTC)
        scan = {
            "scan_id": scan_id,
            "dry_run": dry_run,
            "started_at": started.isoformat(),
            "completed_at": completed.isoformat(),
            "categories_scanned": len(categories),
            "records_scanned": records_scanned,
            "archive_candidates": sum(1 for item in candidates if item["recommended_action"] == RetentionAction.ARCHIVE.value),
            "purge_candidates": sum(1 for item in candidates if item["recommended_action"] == RetentionAction.PURGE.value),
            "legal_hold_records": sum(1 for item in candidates if item["recommended_action"] == RetentionAction.LEGAL_HOLD.value),
            "review_required": sum(1 for item in candidates if item["recommended_action"] == RetentionAction.REVIEW_REQUIRED.value),
            "errors": errors,
            "candidates": candidates,
        }
        store = self._read_store()
        store["scans"].append(scan)
        self._write_store(store)
        audit_service.record_event(None, AuditEventType.RETENTION_SCAN_COMPLETED, "system", ReviewerRole.SYSTEM, metadata={"scan_id": scan_id, "candidate_count": len(candidates), "records_scanned": records_scanned})
        get_telemetry_client().track_event(telemetry_events.RETENTION_SCAN_COMPLETED, {"records_scanned": records_scanned, "candidate_count": len(candidates)})
        return scan

    def _read_store(self) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_store({"scans": []})
        return json.loads(self.path.read_text(encoding="utf-8") or '{"scans":[]}')

    def _write_store(self, payload: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


retention_scanner = RetentionScanner()
