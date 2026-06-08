from datetime import UTC, datetime

from app.compliance.data_classification_registry import CLASSIFICATION_REGISTRY
from app.compliance.retention_config import retention_config
from app.core.constants import DataCategory, DataClassification
from app.services.errors import ApiError


class RetentionPolicyRegistry:
    def __init__(self) -> None:
        self.path = retention_config.resolve_path(retention_config.policy_store_path)

    def list_policies(self) -> list[dict]:
        overrides = {item["data_category"]: item for item in self._read_store().get("policies", [])}
        return [self._merge_policy(category, overrides.get(category.value)) for category in DataCategory]

    def get_policy(self, data_category: str) -> dict:
        category = DataCategory(data_category)
        override = next((item for item in self._read_store().get("policies", []) if item.get("data_category") == category.value), None)
        return self._merge_policy(category, override)

    def update_policy(self, data_category: str, updates: dict, updated_by: str) -> dict:
        policy = self.get_policy(data_category)
        policy.update({key: value for key, value in updates.items() if value is not None})
        policy["last_updated_by"] = updated_by
        policy["last_updated_at"] = datetime.now(UTC).isoformat()
        errors = self.validate_policy(policy)
        if errors:
            raise ApiError(400, "invalid_retention_policy", f"Retention policy validation failed: {'; '.join(errors)}")
        store = self._read_store()
        policies = [item for item in store.get("policies", []) if item.get("data_category") != DataCategory(data_category).value]
        policies.append(policy)
        self._write_store({"policies": sorted(policies, key=lambda item: item["data_category"])})
        return policy

    def reset_policy(self, data_category: str, updated_by: str) -> dict:
        category = DataCategory(data_category)
        store = self._read_store()
        store["policies"] = [item for item in store.get("policies", []) if item.get("data_category") != category.value]
        self._write_store(store)
        policy = self.get_policy(category.value)
        policy["last_updated_by"] = updated_by
        return policy

    def validate_policy(self, policy: dict) -> list[str]:
        errors = []
        if int(policy["retention_days"]) <= 0:
            errors.append("retention_days must be positive.")
        if int(policy["archive_after_days"]) > int(policy["retention_days"]):
            errors.append("archive_after_days must be less than or equal to retention_days.")
        if int(policy["purge_after_days"]) < int(policy["archive_after_days"]):
            errors.append("purge_after_days must be greater than or equal to archive_after_days.")
        if policy.get("data_category") == DataCategory.AUDIT_EVENT.value and int(policy["retention_days"]) < 3650:
            errors.append("audit events should not have short retention by default.")
        if policy.get("auto_purge") and policy.get("requires_approval_for_purge"):
            errors.append("auto_purge cannot be true while purge approval is required.")
        if policy.get("classification") == DataClassification.RESTRICTED.value and int(policy["retention_days"]) < 365:
            errors.append("restricted data retention_days is unusually short.")
        return errors

    def _merge_policy(self, category: DataCategory, override: dict | None = None) -> dict:
        default = self._default_policy(category)
        if override:
            default.update(override)
        default["warnings"] = self.validate_policy(default)
        return default

    def _default_policy(self, category: DataCategory) -> dict:
        classification = CLASSIFICATION_REGISTRY[category][0]
        retention_days = retention_config.default_retention_days()[category]
        archive_after_days = max(1, int(retention_days * retention_config.archive_after_percentage / 100))
        now = datetime.now(UTC).isoformat()
        return {
            "policy_id": f"RET-{category.value.replace('_', '-')}",
            "data_category": category.value,
            "classification": classification.value,
            "retention_days": retention_days,
            "archive_after_days": archive_after_days,
            "purge_after_days": retention_days,
            "auto_archive": False,
            "auto_purge": False,
            "requires_approval_for_archive": retention_config.require_approval_for_archive,
            "requires_approval_for_purge": retention_config.require_approval_for_purge,
            "legal_hold_exempt": False,
            "allow_purge": category != DataCategory.AUDIT_EVENT,
            "description": f"{category.value.replace('_', ' ').title()} retained under MVP placeholder policy.",
            "enabled": True,
            "last_updated_by": "system",
            "last_updated_at": now,
        }

    def _read_store(self) -> dict:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write_store({"policies": []})
        import json

        return json.loads(self.path.read_text(encoding="utf-8") or '{"policies":[]}')

    def _write_store(self, payload: dict) -> None:
        import json

        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


retention_policy_registry = RetentionPolicyRegistry()
