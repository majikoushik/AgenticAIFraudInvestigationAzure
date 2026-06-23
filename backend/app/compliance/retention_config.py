from dataclasses import dataclass
from pathlib import Path

from app.config import settings
from app.core.constants import DataCategory


@dataclass(frozen=True)
class RetentionConfig:
    enabled: bool = settings.data_retention_enabled
    mode: str = settings.data_retention_mode
    policy_store_path: str = settings.retention_policy_store_path
    scan_results_store_path: str = settings.retention_scan_results_store_path
    legal_hold_store_path: str = settings.legal_hold_store_path
    compliance_export_store_path: str = settings.compliance_export_store_path
    archive_store_path: str = settings.archive_store_path
    purge_dry_run_default: bool = settings.purge_dry_run_default
    auto_archive_enabled: bool = settings.retention_auto_archive_enabled
    auto_purge_enabled: bool = settings.retention_auto_purge_enabled
    require_approval_for_purge: bool = settings.retention_require_approval_for_purge
    require_approval_for_archive: bool = settings.retention_require_approval_for_archive
    archive_after_percentage: int = settings.retention_archive_after_percentage
    review_lookahead_days: int = settings.retention_review_lookahead_days
    compliance_export_path: str = settings.compliance_export_path
    compliance_export_include_audit: bool = settings.compliance_export_include_audit
    compliance_export_include_ai_outputs: bool = settings.compliance_export_include_ai_outputs
    compliance_export_include_feedback: bool = settings.compliance_export_include_feedback
    compliance_export_redact_pii: bool = settings.compliance_export_redact_pii
    policy_legally_reviewed: bool = settings.retention_policy_legally_reviewed

    def default_retention_days(self) -> dict[DataCategory, int]:
        return {
            DataCategory.FRAUD_CASE: settings.retention_default_fraud_case_days,
            DataCategory.AUDIT_EVENT: settings.retention_default_audit_event_days,
            DataCategory.HUMAN_REVIEW: settings.retention_default_fraud_case_days,
            DataCategory.AI_INVESTIGATION_OUTPUT: settings.retention_default_ai_output_days,
            DataCategory.AGENT_TRACE: settings.retention_default_agent_trace_days,
            DataCategory.RAG_RETRIEVAL_RECORD: settings.retention_default_agent_trace_days,
            DataCategory.POLICY_DOCUMENT: settings.retention_default_config_history_days,
            DataCategory.HISTORICAL_CASE_DOCUMENT: settings.retention_default_config_history_days,
            DataCategory.FEEDBACK_RECORD: settings.retention_default_feedback_days,
            DataCategory.NOTIFICATION_RECORD: settings.retention_default_notification_days,
            DataCategory.INCIDENT_RECORD: settings.retention_default_incident_days,
            DataCategory.ALERT_RECORD: settings.retention_default_incident_days,
            DataCategory.COST_RECORD: settings.retention_default_cost_record_days,
            DataCategory.TELEMETRY_RECORD: settings.retention_default_telemetry_days,
            DataCategory.CONFIG_HISTORY: settings.retention_default_config_history_days,
            DataCategory.ASSIGNMENT_HISTORY: settings.retention_default_config_history_days,
            DataCategory.EXPORT_FILE: settings.retention_default_config_history_days,
        }

    def resolve_path(self, path: str) -> Path:
        configured = Path(path)
        if configured.is_absolute():
            return configured
        parts = configured.parts
        if len(parts) >= 2 and parts[0] == "data" and parts[1] == "synthetic":
            from app.config import get_synthetic_data_path
            return get_synthetic_data_path().joinpath(*parts[2:])
        return (Path(__file__).resolve().parents[3] / configured).resolve()

    def safe_summary(self) -> dict:
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "purge_dry_run_default": self.purge_dry_run_default,
            "auto_archive_enabled": self.auto_archive_enabled,
            "auto_purge_enabled": self.auto_purge_enabled,
            "require_approval_for_purge": self.require_approval_for_purge,
            "require_approval_for_archive": self.require_approval_for_archive,
            "archive_after_percentage": self.archive_after_percentage,
            "review_lookahead_days": self.review_lookahead_days,
            "compliance_export_redact_pii": self.compliance_export_redact_pii,
            "policy_legally_reviewed": self.policy_legally_reviewed,
            "policy_review_warning": None if self.policy_legally_reviewed else "Default retention periods are placeholders and require legal/compliance approval before production use.",
        }


retention_config = RetentionConfig()
