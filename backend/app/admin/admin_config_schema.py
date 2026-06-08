from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ConfigDefinition:
    key: str
    category: str
    data_type: str
    default_value: Any
    editable: bool
    secret: bool
    description: str
    allowed_values: list[Any] | None = None
    min_value: float | None = None
    max_value: float | None = None
    requires_restart: bool = False
    display: bool = True


def _item(key: str, category: str, data_type: str, default: Any, description: str, editable: bool = True, allowed: list[Any] | None = None, min_value: float | None = None, max_value: float | None = None, requires_restart: bool = False) -> ConfigDefinition:
    return ConfigDefinition(key, category, data_type, default, editable, False, description, allowed, min_value, max_value, requires_restart)


SAFE_CONFIG_REGISTRY: dict[str, ConfigDefinition] = {
    "AI_PROVIDER": _item("AI_PROVIDER", "AI_PROVIDER", "enum", "local", "Active AI provider.", allowed=["local", "azure_openai", "foundry_agent_service"]),
    "AI_PROVIDER_ALLOW_FALLBACK": _item("AI_PROVIDER_ALLOW_FALLBACK", "AI_PROVIDER", "boolean", True, "Allow fallback to local deterministic provider."),
    "LLM_ENABLE_JSON_MODE": _item("LLM_ENABLE_JSON_MODE", "AI_PROVIDER", "boolean", True, "Request JSON mode from supported LLM providers."),
    "LLM_ENABLE_STREAMING": _item("LLM_ENABLE_STREAMING", "AI_PROVIDER", "boolean", False, "Enable streaming responses where supported."),
    "AI_SAFETY_REQUIRE_HUMAN_REVIEW": _item("AI_SAFETY_REQUIRE_HUMAN_REVIEW", "AI_PROVIDER", "boolean", True, "Require human review for high-impact AI outputs."),
    "AI_SAFETY_REQUIRE_CITATIONS": _item("AI_SAFETY_REQUIRE_CITATIONS", "AI_PROVIDER", "boolean", True, "Require policy citations where applicable."),
    "AI_SAFETY_MAX_RECOMMENDATION_CONFIDENCE": _item("AI_SAFETY_MAX_RECOMMENDATION_CONFIDENCE", "AI_PROVIDER", "enum", "HIGH", "Maximum AI recommendation confidence label.", allowed=["LOW", "MEDIUM", "HIGH"]),
    "AZURE_OPENAI_CHAT_DEPLOYMENT": _item("AZURE_OPENAI_CHAT_DEPLOYMENT", "AZURE_OPENAI_FOUNDRY", "string", "gpt-4o-mini", "Azure OpenAI chat deployment name.", requires_restart=True),
    "AZURE_OPENAI_REASONING_DEPLOYMENT": _item("AZURE_OPENAI_REASONING_DEPLOYMENT", "AZURE_OPENAI_FOUNDRY", "string", "", "Azure OpenAI reasoning deployment name.", requires_restart=True),
    "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": _item("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "AZURE_OPENAI_FOUNDRY", "string", "text-embedding-3-small", "Azure OpenAI embedding deployment name.", requires_restart=True),
    "AZURE_OPENAI_API_VERSION": _item("AZURE_OPENAI_API_VERSION", "AZURE_OPENAI_FOUNDRY", "string", "2024-12-01-preview", "Azure OpenAI API version.", requires_restart=True),
    "AZURE_OPENAI_REQUEST_TIMEOUT_SECONDS": _item("AZURE_OPENAI_REQUEST_TIMEOUT_SECONDS", "AZURE_OPENAI_FOUNDRY", "integer", 60, "Azure OpenAI request timeout.", min_value=1, max_value=300),
    "AZURE_OPENAI_MAX_RETRIES": _item("AZURE_OPENAI_MAX_RETRIES", "AZURE_OPENAI_FOUNDRY", "integer", 3, "Azure OpenAI retry count.", min_value=0, max_value=10),
    "AZURE_OPENAI_TEMPERATURE": _item("AZURE_OPENAI_TEMPERATURE", "AZURE_OPENAI_FOUNDRY", "float", 0.2, "Azure OpenAI temperature.", min_value=0, max_value=2),
    "AZURE_OPENAI_MAX_TOKENS": _item("AZURE_OPENAI_MAX_TOKENS", "AZURE_OPENAI_FOUNDRY", "integer", 2000, "Azure OpenAI max output tokens.", min_value=1, max_value=128000),
    "USE_AZURE_AI_FOUNDRY_AGENT_SERVICE": _item("USE_AZURE_AI_FOUNDRY_AGENT_SERVICE", "AZURE_OPENAI_FOUNDRY", "boolean", False, "Enable Azure AI Foundry Agent Service placeholder."),
    "USE_AZURE_SEARCH": _item("USE_AZURE_SEARCH", "RAG", "boolean", False, "Use Azure AI Search for RAG retrieval."),
    "AZURE_SEARCH_POLICY_INDEX": _item("AZURE_SEARCH_POLICY_INDEX", "RAG", "string", "fraud-policies", "Policy index name."),
    "AZURE_SEARCH_HISTORICAL_CASE_INDEX": _item("AZURE_SEARCH_HISTORICAL_CASE_INDEX", "RAG", "string", "historical-fraud-cases", "Historical case index name."),
    "AZURE_SEARCH_EVIDENCE_INDEX": _item("AZURE_SEARCH_EVIDENCE_INDEX", "RAG", "string", "case-evidence", "Case evidence index name."),
    "RAG_CHUNK_SIZE": _item("RAG_CHUNK_SIZE", "RAG", "integer", 1000, "RAG chunk size.", min_value=100, max_value=5000),
    "RAG_CHUNK_OVERLAP": _item("RAG_CHUNK_OVERLAP", "RAG", "integer", 150, "RAG chunk overlap.", min_value=0, max_value=1000),
    "RAG_TOP_K": _item("RAG_TOP_K", "RAG", "integer", 5, "Number of top retrieved documents.", min_value=1, max_value=20),
    "RAG_ENABLE_HYBRID_SEARCH": _item("RAG_ENABLE_HYBRID_SEARCH", "RAG", "boolean", True, "Enable hybrid RAG retrieval."),
    "RAG_ENABLE_SEMANTIC_RANKER": _item("RAG_ENABLE_SEMANTIC_RANKER", "RAG", "boolean", False, "Enable semantic ranker where available."),
    "HUMAN_REVIEW_REQUIRED": _item("HUMAN_REVIEW_REQUIRED", "HUMAN_REVIEW", "boolean", True, "Require human review before final decisions."),
    "ALLOW_REINVESTIGATION": _item("ALLOW_REINVESTIGATION", "HUMAN_REVIEW", "boolean", False, "Allow reinvestigation after initial review."),
    "REQUIRE_EVIDENCE_ACKNOWLEDGEMENT": _item("REQUIRE_EVIDENCE_ACKNOWLEDGEMENT", "HUMAN_REVIEW", "boolean", True, "Require evidence acknowledgement."),
    "REQUIRE_POLICY_ACKNOWLEDGEMENT": _item("REQUIRE_POLICY_ACKNOWLEDGEMENT", "HUMAN_REVIEW", "boolean", True, "Require policy acknowledgement."),
    "REQUIRE_OVERRIDE_REASON": _item("REQUIRE_OVERRIDE_REASON", "HUMAN_REVIEW", "boolean", True, "Require override reason."),
    "MIN_REVIEW_COMMENT_LENGTH": _item("MIN_REVIEW_COMMENT_LENGTH", "HUMAN_REVIEW", "integer", 10, "Minimum review comment length.", min_value=0, max_value=1000),
    "ALERTING_ENABLED": _item("ALERTING_ENABLED", "ALERTING", "boolean", True, "Enable alerting."),
    "ALERT_HIGH_API_ERROR_RATE_THRESHOLD_PERCENT": _item("ALERT_HIGH_API_ERROR_RATE_THRESHOLD_PERCENT", "ALERTING", "float", 5, "High API error rate threshold.", min_value=0, max_value=100),
    "ALERT_HIGH_API_LATENCY_THRESHOLD_MS": _item("ALERT_HIGH_API_LATENCY_THRESHOLD_MS", "ALERTING", "integer", 3000, "High API latency threshold.", min_value=1, max_value=600000),
    "ALERT_HIGH_AGENT_FAILURE_COUNT": _item("ALERT_HIGH_AGENT_FAILURE_COUNT", "ALERTING", "integer", 5, "High agent failure count threshold.", min_value=1, max_value=10000),
    "ALERT_HIGH_RAG_EMPTY_RESULT_COUNT": _item("ALERT_HIGH_RAG_EMPTY_RESULT_COUNT", "ALERTING", "integer", 10, "High RAG empty result count threshold.", min_value=1, max_value=10000),
    "ALERT_HIGH_LLM_LATENCY_THRESHOLD_MS": _item("ALERT_HIGH_LLM_LATENCY_THRESHOLD_MS", "ALERTING", "integer", 8000, "High LLM latency threshold.", min_value=1, max_value=600000),
    "ALERT_HIGH_TOKEN_USAGE_THRESHOLD": _item("ALERT_HIGH_TOKEN_USAGE_THRESHOLD", "ALERTING", "integer", 100000, "High token usage threshold.", min_value=1, max_value=1000000000),
    "ALERT_HIGH_HUMAN_OVERRIDE_RATE_PERCENT": _item("ALERT_HIGH_HUMAN_OVERRIDE_RATE_PERCENT", "ALERTING", "float", 40, "High human override rate threshold.", min_value=0, max_value=100),
    "ALERT_POLICY_CITATION_ACCURACY_MIN_PERCENT": _item("ALERT_POLICY_CITATION_ACCURACY_MIN_PERCENT", "ALERTING", "float", 80, "Minimum policy citation accuracy.", min_value=0, max_value=100),
    "ALERT_STUCK_PENDING_REVIEW_HOURS": _item("ALERT_STUCK_PENDING_REVIEW_HOURS", "ALERTING", "integer", 24, "Pending review age threshold.", min_value=1, max_value=8760),
    "COST_MONITORING_ENABLED": _item("COST_MONITORING_ENABLED", "COST_MONITORING", "boolean", True, "Enable cost monitoring."),
    "CURRENCY": _item("CURRENCY", "COST_MONITORING", "enum", "USD", "Currency code for cost estimates.", allowed=["USD", "EUR", "GBP", "INR"]),
    "DEFAULT_INPUT_TOKEN_COST_PER_1K": _item("DEFAULT_INPUT_TOKEN_COST_PER_1K", "COST_MONITORING", "float", 0.0, "Default input token cost per 1K.", min_value=0, max_value=1000),
    "DEFAULT_OUTPUT_TOKEN_COST_PER_1K": _item("DEFAULT_OUTPUT_TOKEN_COST_PER_1K", "COST_MONITORING", "float", 0.0, "Default output token cost per 1K.", min_value=0, max_value=1000),
    "TOKEN_DAILY_LIMIT": _item("TOKEN_DAILY_LIMIT", "COST_MONITORING", "integer", 1000000, "Daily token limit.", min_value=0, max_value=1000000000),
    "COST_DAILY_BUDGET_LIMIT": _item("COST_DAILY_BUDGET_LIMIT", "COST_MONITORING", "float", 50, "Daily cost budget.", min_value=0, max_value=10000000),
    "COST_MONTHLY_BUDGET_LIMIT": _item("COST_MONTHLY_BUDGET_LIMIT", "COST_MONITORING", "float", 1000, "Monthly cost budget.", min_value=0, max_value=100000000),
    "TOKEN_PER_CASE_WARNING_THRESHOLD": _item("TOKEN_PER_CASE_WARNING_THRESHOLD", "COST_MONITORING", "integer", 25000, "Per-case token warning threshold.", min_value=0, max_value=100000000),
    "COST_PER_CASE_WARNING_THRESHOLD": _item("COST_PER_CASE_WARNING_THRESHOLD", "COST_MONITORING", "float", 2.0, "Per-case cost warning threshold.", min_value=0, max_value=1000000),
    "COST_ANOMALY_PERCENT_INCREASE_THRESHOLD": _item("COST_ANOMALY_PERCENT_INCREASE_THRESHOLD", "COST_MONITORING", "float", 50, "Cost anomaly percent increase threshold.", min_value=0, max_value=10000),
    "OBSERVABILITY_ENABLED": _item("OBSERVABILITY_ENABLED", "OBSERVABILITY", "boolean", True, "Enable observability."),
    "OBSERVABILITY_MODE": _item("OBSERVABILITY_MODE", "OBSERVABILITY", "enum", "local", "Observability mode.", allowed=["local", "azure_monitor"]),
    "LOG_LEVEL": _item("LOG_LEVEL", "OBSERVABILITY", "enum", "INFO", "Log level.", allowed=["DEBUG", "INFO", "WARNING", "ERROR"]),
    "LOG_FORMAT": _item("LOG_FORMAT", "OBSERVABILITY", "enum", "json", "Log format.", allowed=["json", "text"]),
    "TELEMETRY_ENVIRONMENT": _item("TELEMETRY_ENVIRONMENT", "OBSERVABILITY", "string", "local", "Telemetry environment name."),
    "TELEMETRY_SAMPLE_RATE": _item("TELEMETRY_SAMPLE_RATE", "OBSERVABILITY", "float", 1.0, "Telemetry sample rate.", min_value=0, max_value=1),
    "TELEMETRY_ENABLE_API": _item("TELEMETRY_ENABLE_API", "OBSERVABILITY", "boolean", True, "Emit API telemetry."),
    "TELEMETRY_ENABLE_AGENT": _item("TELEMETRY_ENABLE_AGENT", "OBSERVABILITY", "boolean", True, "Emit agent telemetry."),
    "TELEMETRY_ENABLE_RAG": _item("TELEMETRY_ENABLE_RAG", "OBSERVABILITY", "boolean", True, "Emit RAG telemetry."),
    "TELEMETRY_ENABLE_LLM": _item("TELEMETRY_ENABLE_LLM", "OBSERVABILITY", "boolean", True, "Emit LLM telemetry."),
    "TELEMETRY_ENABLE_BUSINESS": _item("TELEMETRY_ENABLE_BUSINESS", "OBSERVABILITY", "boolean", True, "Emit business telemetry."),
    "TELEMETRY_ENABLE_SECURITY": _item("TELEMETRY_ENABLE_SECURITY", "OBSERVABILITY", "boolean", True, "Emit security telemetry."),
    "CASE_ASSIGNMENT_ENABLED": _item("CASE_ASSIGNMENT_ENABLED", "CASE_ASSIGNMENT", "boolean", True, "Enable local case assignment and queue APIs."),
    "DEFAULT_ASSIGNMENT_TEAM": _item("DEFAULT_ASSIGNMENT_TEAM", "CASE_ASSIGNMENT", "string", "Fraud Operations", "Default assignment team."),
    "DEFAULT_ASSIGNMENT_PRIORITY": _item("DEFAULT_ASSIGNMENT_PRIORITY", "CASE_ASSIGNMENT", "enum", "MEDIUM", "Default assignment priority.", allowed=["LOW", "MEDIUM", "HIGH", "CRITICAL"]),
    "SLA_LOW_PRIORITY_HOURS": _item("SLA_LOW_PRIORITY_HOURS", "CASE_ASSIGNMENT", "integer", 72, "SLA hours for low priority cases.", min_value=1, max_value=720),
    "SLA_MEDIUM_PRIORITY_HOURS": _item("SLA_MEDIUM_PRIORITY_HOURS", "CASE_ASSIGNMENT", "integer", 48, "SLA hours for medium priority cases.", min_value=1, max_value=720),
    "SLA_HIGH_PRIORITY_HOURS": _item("SLA_HIGH_PRIORITY_HOURS", "CASE_ASSIGNMENT", "integer", 24, "SLA hours for high priority cases.", min_value=1, max_value=720),
    "SLA_CRITICAL_PRIORITY_HOURS": _item("SLA_CRITICAL_PRIORITY_HOURS", "CASE_ASSIGNMENT", "integer", 4, "SLA hours for critical priority cases.", min_value=1, max_value=168),
    "AUTO_SET_SLA_ON_ASSIGNMENT": _item("AUTO_SET_SLA_ON_ASSIGNMENT", "CASE_ASSIGNMENT", "boolean", True, "Automatically set SLA due date during assignment."),
    "ALLOW_SELF_ASSIGNMENT": _item("ALLOW_SELF_ASSIGNMENT", "CASE_ASSIGNMENT", "boolean", True, "Allow analysts to self-assign unassigned cases."),
    "ALLOW_ANALYST_RELEASE_OWN_CASE": _item("ALLOW_ANALYST_RELEASE_OWN_CASE", "CASE_ASSIGNMENT", "boolean", True, "Allow analysts to release their own cases."),
    "ALLOW_ANALYST_TRANSFER_REQUEST": _item("ALLOW_ANALYST_TRANSFER_REQUEST", "CASE_ASSIGNMENT", "boolean", False, "Allow analyst transfer requests when workflow is implemented."),
    "MAX_ACTIVE_CASES_PER_INVESTIGATOR": _item("MAX_ACTIVE_CASES_PER_INVESTIGATOR", "CASE_ASSIGNMENT", "integer", 20, "Maximum target active cases per investigator.", min_value=1, max_value=200),
    "WORKLOAD_HIGH_THRESHOLD": _item("WORKLOAD_HIGH_THRESHOLD", "CASE_ASSIGNMENT", "integer", 15, "High workload threshold.", min_value=1, max_value=200),
    "WORKLOAD_CRITICAL_THRESHOLD": _item("WORKLOAD_CRITICAL_THRESHOLD", "CASE_ASSIGNMENT", "integer", 20, "Critical workload threshold.", min_value=1, max_value=200),
}


FEATURE_FLAG_KEYS = [
    "FEATURE_ENABLE_AGENTIC_INVESTIGATION",
    "FEATURE_ENABLE_HUMAN_REVIEW",
    "FEATURE_ENABLE_OVERRIDE_TRACKING",
    "FEATURE_ENABLE_COST_DASHBOARD",
    "FEATURE_ENABLE_OBSERVABILITY_PAGE",
    "FEATURE_ENABLE_ALERT_SIMULATION",
    "FEATURE_ENABLE_CASE_ASSIGNMENT",
    "FEATURE_ENABLE_LOCAL_DEMO_MODE",
    "FEATURE_ENABLE_AZURE_SEARCH_RAG",
    "FEATURE_ENABLE_AZURE_OPENAI",
]

for flag in FEATURE_FLAG_KEYS:
    SAFE_CONFIG_REGISTRY[flag] = _item(flag, "FEATURE_FLAGS", "boolean", flag not in {"FEATURE_ENABLE_AZURE_SEARCH_RAG", "FEATURE_ENABLE_AZURE_OPENAI"}, flag.replace("_", " ").title().capitalize())
