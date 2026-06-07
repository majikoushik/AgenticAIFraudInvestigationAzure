import os
from dataclasses import dataclass, field


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() == "true"


@dataclass(frozen=True)
class AlertingConfig:
    alerting_enabled: bool = field(default_factory=lambda: _bool("ALERTING_ENABLED", True))
    alerting_mode: str = field(default_factory=lambda: os.getenv("ALERTING_MODE", "local"))
    incidents_local_store_path: str = field(default_factory=lambda: os.getenv("INCIDENTS_LOCAL_STORE_PATH", "data/synthetic/incidents.json"))
    alerts_local_store_path: str = field(default_factory=lambda: os.getenv("ALERTS_LOCAL_STORE_PATH", "data/synthetic/alerts.json"))
    high_api_error_rate_threshold_percent: float = field(default_factory=lambda: float(os.getenv("ALERT_HIGH_API_ERROR_RATE_THRESHOLD_PERCENT", "5")))
    high_api_latency_threshold_ms: float = field(default_factory=lambda: float(os.getenv("ALERT_HIGH_API_LATENCY_THRESHOLD_MS", "3000")))
    high_agent_failure_count: int = field(default_factory=lambda: int(os.getenv("ALERT_HIGH_AGENT_FAILURE_COUNT", "5")))
    high_rag_empty_result_count: int = field(default_factory=lambda: int(os.getenv("ALERT_HIGH_RAG_EMPTY_RESULT_COUNT", "10")))
    high_llm_latency_threshold_ms: float = field(default_factory=lambda: float(os.getenv("ALERT_HIGH_LLM_LATENCY_THRESHOLD_MS", "8000")))
    high_token_usage_threshold: int = field(default_factory=lambda: int(os.getenv("ALERT_HIGH_TOKEN_USAGE_THRESHOLD", "100000")))
    high_human_override_rate_percent: float = field(default_factory=lambda: float(os.getenv("ALERT_HIGH_HUMAN_OVERRIDE_RATE_PERCENT", "40")))
    policy_citation_accuracy_min_percent: float = field(default_factory=lambda: float(os.getenv("ALERT_POLICY_CITATION_ACCURACY_MIN_PERCENT", "80")))
    stuck_pending_review_hours: int = field(default_factory=lambda: int(os.getenv("ALERT_STUCK_PENDING_REVIEW_HOURS", "24")))
    notifications_enabled: bool = field(default_factory=lambda: _bool("NOTIFICATIONS_ENABLED", False))
    notification_mode: str = field(default_factory=lambda: os.getenv("NOTIFICATION_MODE", "local"))
    teams_webhook_configured: bool = field(default_factory=lambda: bool(os.getenv("TEAMS_WEBHOOK_URL", "")))
    email_configured: bool = field(default_factory=lambda: bool(os.getenv("EMAIL_SMTP_HOST", "") and os.getenv("ALERT_EMAIL_RECIPIENTS", "")))
    default_incident_owner: str = field(default_factory=lambda: os.getenv("INCIDENT_AUTO_ASSIGN_DEFAULT_OWNER", "platform-operations"))
    incident_auto_create_enabled: bool = field(default_factory=lambda: _bool("INCIDENT_AUTO_CREATE_ENABLED", True))

    @property
    def thresholds(self) -> dict[str, float | int]:
        return {
            "high_api_error_rate_threshold_percent": self.high_api_error_rate_threshold_percent,
            "high_api_latency_threshold_ms": self.high_api_latency_threshold_ms,
            "high_agent_failure_count": self.high_agent_failure_count,
            "high_rag_empty_result_count": self.high_rag_empty_result_count,
            "high_llm_latency_threshold_ms": self.high_llm_latency_threshold_ms,
            "high_token_usage_threshold": self.high_token_usage_threshold,
            "high_human_override_rate_percent": self.high_human_override_rate_percent,
            "policy_citation_accuracy_min_percent": self.policy_citation_accuracy_min_percent,
            "stuck_pending_review_hours": self.stuck_pending_review_hours,
        }

    def safe_summary(self) -> dict:
        return {
            "alerting_enabled": self.alerting_enabled,
            "alerting_mode": self.alerting_mode,
            "thresholds": self.thresholds,
            "notifications_enabled": self.notifications_enabled,
            "notification_mode": self.notification_mode,
            "teams_webhook_configured": self.teams_webhook_configured,
            "email_configured": self.email_configured,
            "default_incident_owner": self.default_incident_owner,
            "incident_auto_create_enabled": self.incident_auto_create_enabled,
        }


alerting_config = AlertingConfig()
