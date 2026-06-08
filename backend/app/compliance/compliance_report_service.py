from app.compliance.legal_hold_service import legal_hold_service
from app.compliance.retention_policy_registry import retention_policy_registry
from app.compliance.retention_repository import SOURCE_MAP, retention_repository
from app.compliance.retention_scanner import retention_scanner
from app.compliance.compliance_export_service import compliance_export_service


class ComplianceReportService:
    def get_retention_summary(self) -> dict:
        candidates = retention_scanner.latest_candidates()
        latest_scan = None
        try:
            scans = retention_scanner._read_store()["scans"]
            latest_scan = scans[-1]["completed_at"] if scans else None
        except Exception:
            latest_scan = None
        return {
            "total_records_by_category": {category.value: len(retention_repository.list_records_by_category(category.value)) for category in SOURCE_MAP},
            "archive_candidates": sum(1 for item in candidates if item.get("recommended_action") == "ARCHIVE"),
            "purge_candidates": sum(1 for item in candidates if item.get("recommended_action") == "PURGE"),
            "review_required_count": sum(1 for item in candidates if item.get("recommended_action") == "REVIEW_REQUIRED"),
            "legal_hold_count": len(legal_hold_service.list_legal_holds(status="ACTIVE")),
            "latest_scan_timestamp": latest_scan,
        }

    def get_compliance_summary(self) -> dict:
        policies = retention_policy_registry.list_policies()
        retention = self.get_retention_summary()
        return {
            **retention,
            "exports_generated": len(compliance_export_service.list_exports()),
            "policy_count": len(policies),
            "disabled_policies": sum(1 for item in policies if not item.get("enabled")),
            "compliance_warnings": ["Retention defaults are placeholders and must be approved by legal/compliance before production use."],
        }

    def get_legal_hold_summary(self) -> dict:
        holds = legal_hold_service.list_legal_holds()
        return {"total_holds": len(holds), "active_holds": sum(1 for item in holds if item.get("status") == "ACTIVE"), "released_holds": sum(1 for item in holds if item.get("status") == "RELEASED")}


compliance_report_service = ComplianceReportService()
