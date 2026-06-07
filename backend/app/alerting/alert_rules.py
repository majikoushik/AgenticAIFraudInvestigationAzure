from app.alerting.alert_config import alerting_config
from app.alerting.runbook_registry import get_runbook_for_alert
from app.core.constants import AlertSeverity, AlertType


def build_rule(alert_type: AlertType, severity: AlertSeverity, title: str, description: str, metric_name: str, threshold_value: float) -> dict:
    return {
        "alert_type": alert_type.value,
        "severity": severity.value,
        "title": title,
        "description": description,
        "metric_name": metric_name,
        "threshold_value": threshold_value,
        "recommended_runbook": get_runbook_for_alert(alert_type.value),
    }


def alert_rules() -> list[dict]:
    return [
        build_rule(AlertType.HIGH_API_ERROR_RATE, AlertSeverity.SEV1_HIGH, "High API error rate detected", "API 5xx responses exceeded the configured threshold.", "api_error_rate_percentage", alerting_config.high_api_error_rate_threshold_percent),
        build_rule(AlertType.HIGH_API_LATENCY, AlertSeverity.SEV2_MEDIUM, "High API latency detected", "Average API request latency exceeded the configured threshold.", "api_latency_ms", alerting_config.high_api_latency_threshold_ms),
        build_rule(AlertType.HIGH_AGENT_FAILURE_RATE, AlertSeverity.SEV1_HIGH, "High agent failure rate detected", "Agent failures exceeded the configured threshold.", "agent_failure_count", alerting_config.high_agent_failure_count),
        build_rule(AlertType.HIGH_RAG_EMPTY_RESULT_RATE, AlertSeverity.SEV2_MEDIUM, "High RAG empty result rate detected", "RAG empty retrievals exceeded the configured threshold.", "rag_empty_result_count", alerting_config.high_rag_empty_result_count),
        build_rule(AlertType.CITATION_VALIDATION_FAILURE, AlertSeverity.SEV1_HIGH, "Citation validation failure detected", "One or more policy citations failed validation.", "citation_validation_failure_count", 1),
        build_rule(AlertType.HIGH_LLM_LATENCY, AlertSeverity.SEV2_MEDIUM, "High LLM latency detected", "Average LLM latency exceeded the configured threshold.", "llm_latency_ms", alerting_config.high_llm_latency_threshold_ms),
        build_rule(AlertType.HIGH_TOKEN_USAGE, AlertSeverity.SEV2_MEDIUM, "High token usage detected", "Token usage exceeded the configured threshold.", "total_tokens", alerting_config.high_token_usage_threshold),
        build_rule(AlertType.HIGH_COST_ESTIMATE, AlertSeverity.SEV2_MEDIUM, "High estimated AI cost detected", "Estimated local AI cost exceeded the configured threshold.", "daily_estimated_cost", 1),
        build_rule(AlertType.BUDGET_WARNING, AlertSeverity.SEV2_MEDIUM, "Cost budget warning", "Cost or token budget usage reached warning level.", "budget_used_percentage", 80),
        build_rule(AlertType.BUDGET_EXCEEDED, AlertSeverity.SEV1_HIGH, "Cost budget exceeded", "Cost or token budget limit was exceeded.", "budget_used_percentage", 100),
        build_rule(AlertType.COST_ANOMALY_DETECTED, AlertSeverity.SEV1_HIGH, "Cost anomaly detected", "Daily cost or token usage anomaly was detected.", "cost_anomaly", 1),
        build_rule(AlertType.HIGH_CASE_COST_DETECTED, AlertSeverity.SEV2_MEDIUM, "High case cost detected", "One or more cases exceeded the configured per-case cost threshold.", "case_estimated_cost", 1),
        build_rule(AlertType.HIGH_AGENT_COST_DETECTED, AlertSeverity.SEV2_MEDIUM, "High agent cost detected", "Agent cost is elevated compared with local thresholds.", "agent_estimated_cost", 1),
        build_rule(AlertType.PROMPT_INJECTION_DETECTED, AlertSeverity.SEV0_CRITICAL, "Prompt injection detected", "Prompt injection signals were detected in input or retrieved content.", "prompt_injection_count", 1),
        build_rule(AlertType.GUARDRAIL_VIOLATION_DETECTED, AlertSeverity.SEV1_HIGH, "Guardrail violation detected", "AI safety guardrail violations were detected.", "guardrail_violation_count", 1),
        build_rule(AlertType.HIGH_HUMAN_OVERRIDE_RATE, AlertSeverity.SEV1_HIGH, "High human override rate detected", "Human override rate exceeded the configured threshold.", "override_rate_percentage", alerting_config.high_human_override_rate_percent),
        build_rule(AlertType.CASES_STUCK_PENDING_REVIEW, AlertSeverity.SEV1_HIGH, "Cases stuck pending review", "Cases remained in pending review beyond the configured threshold.", "stuck_pending_review_count", 1),
        build_rule(AlertType.POLICY_CITATION_ACCURACY_LOW, AlertSeverity.SEV2_MEDIUM, "Policy citation accuracy low", "Policy citation rate is below the configured threshold.", "policy_citation_accuracy_percentage", alerting_config.policy_citation_accuracy_min_percent),
    ]
