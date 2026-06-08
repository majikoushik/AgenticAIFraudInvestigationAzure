from datetime import UTC, datetime

from app.compliance.legal_hold_service import legal_hold_service
from app.compliance.retention_config import retention_config
from app.compliance.retention_repository import retention_repository
from app.compliance.retention_scanner import retention_scanner
from app.core.constants import AuditEventType, RetentionAction, ReviewerRole
from app.services.audit_service import audit_service


class ArchivalService:
    def archive_candidates(self, scan_id: str, approved_by: str, dry_run: bool = True, record_ids: list[str] | None = None) -> dict:
        scan = retention_scanner.get_scan(scan_id)
        candidates = [item for item in scan.get("candidates", []) if item.get("recommended_action") == RetentionAction.ARCHIVE.value]
        if record_ids:
            candidates = [item for item in candidates if item["record_id"] in record_ids]
        return self._process(candidates, approved_by, dry_run)

    def archive_record(self, data_category: str, record_id: str, approved_by: str, dry_run: bool = True) -> dict:
        return self._process([{"data_category": data_category, "record_id": record_id, "case_id": None}], approved_by, dry_run)

    def _process(self, candidates: list[dict], approved_by: str, dry_run: bool) -> dict:
        results = []
        for item in candidates:
            if legal_hold_service.is_record_under_legal_hold(item["data_category"], item["record_id"], item.get("case_id")):
                results.append({"record_id": item["record_id"], "blocked": True, "reason": "Legal hold active."})
                continue
            if dry_run:
                results.append({"record_id": item["record_id"], "data_category": item["data_category"], "dry_run": True, "would_archive": True})
                continue
            year = datetime.now(UTC).strftime("%Y")
            archive_path = retention_config.resolve_path(f"{retention_config.archive_store_path}/{item['data_category']}/{year}/{item['record_id']}.json")
            results.append(retention_repository.archive_record(item["data_category"], item["record_id"], str(archive_path)))
        audit_service.record_event(None, AuditEventType.RETENTION_ARCHIVE_DRY_RUN if dry_run else AuditEventType.RETENTION_ARCHIVE_EXECUTED, approved_by, ReviewerRole.COMPLIANCE_OFFICER, metadata={"candidate_count": len(candidates), "dry_run": dry_run})
        return {"action": RetentionAction.ARCHIVE.value, "dry_run": dry_run, "requested_by": approved_by, "processed_count": len(results), "blocked_count": sum(1 for item in results if item.get("blocked")), "results": results}


archival_service = ArchivalService()
