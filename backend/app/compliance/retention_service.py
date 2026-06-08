from app.compliance.retention_policy_registry import retention_policy_registry
from app.compliance.retention_scanner import retention_scanner
from app.compliance.retention_review_service import retention_review_service


class RetentionService:
    def list_policies(self) -> list[dict]:
        return retention_policy_registry.list_policies()

    def get_policy(self, data_category: str) -> dict:
        return retention_policy_registry.get_policy(data_category)

    def scan(self, data_category: str | None = None, dry_run: bool = True) -> dict:
        return retention_scanner.scan_category(data_category, dry_run) if data_category else retention_scanner.scan_all(dry_run)

    def get_scan(self, scan_id: str) -> dict:
        return retention_scanner.get_scan(scan_id)

    def get_review_queue(self, filters: dict | None = None) -> dict:
        return retention_review_service.get_review_queue(filters)


retention_service = RetentionService()
