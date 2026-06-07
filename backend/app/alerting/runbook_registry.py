from app.core.constants import AlertType


RUNBOOKS = {
    AlertType.HIGH_API_ERROR_RATE: "docs/runbooks/high-api-error-rate.md",
    AlertType.HIGH_API_LATENCY: "docs/runbooks/high-api-latency.md",
    AlertType.HIGH_AGENT_FAILURE_RATE: "docs/runbooks/agent-failure.md",
    AlertType.AGENT_EXECUTION_TIMEOUT: "docs/runbooks/agent-timeout.md",
    AlertType.HIGH_RAG_EMPTY_RESULT_RATE: "docs/runbooks/rag-empty-results.md",
    AlertType.CITATION_VALIDATION_FAILURE: "docs/runbooks/citation-validation-failure.md",
    AlertType.POLICY_CITATION_ACCURACY_LOW: "docs/runbooks/low-policy-citation-accuracy.md",
    AlertType.HIGH_LLM_LATENCY: "docs/runbooks/high-llm-latency.md",
    AlertType.HIGH_LLM_FAILURE_RATE: "docs/runbooks/llm-failure.md",
    AlertType.HIGH_TOKEN_USAGE: "docs/runbooks/high-token-usage.md",
    AlertType.HIGH_COST_ESTIMATE: "docs/runbooks/high-cost-estimate.md",
    AlertType.HIGH_HUMAN_OVERRIDE_RATE: "docs/runbooks/high-human-override-rate.md",
    AlertType.CASES_STUCK_PENDING_REVIEW: "docs/runbooks/stuck-pending-review-cases.md",
    AlertType.PROMPT_INJECTION_DETECTED: "docs/runbooks/prompt-injection-detected.md",
    AlertType.GUARDRAIL_VIOLATION_DETECTED: "docs/runbooks/guardrail-violation.md",
    AlertType.AUDIT_LOG_WRITE_FAILURE: "docs/runbooks/audit-log-write-failure.md",
}


def get_runbook_for_alert(alert_type: str) -> str:
    try:
        return RUNBOOKS.get(AlertType(alert_type), "docs/runbooks/general-incident-response.md")
    except ValueError:
        return "docs/runbooks/general-incident-response.md"
