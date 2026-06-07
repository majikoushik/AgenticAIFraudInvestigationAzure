import os
from dataclasses import dataclass


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() == "true"


@dataclass(frozen=True)
class ObservabilityConfig:
    enabled: bool = _bool("OBSERVABILITY_ENABLED", True)
    mode: str = os.getenv("OBSERVABILITY_MODE", "local")
    applicationinsights_connection_string: str = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
    applicationinsights_instrumentation_key: str = os.getenv("APPLICATIONINSIGHTS_INSTRUMENTATION_KEY", "")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    service_name: str = os.getenv("TELEMETRY_SERVICE_NAME", "fraud-investigation-platform")
    environment: str = os.getenv("TELEMETRY_ENVIRONMENT", os.getenv("ENVIRONMENT", "local"))
    sample_rate: float = float(os.getenv("TELEMETRY_SAMPLE_RATE", "1.0"))
    enable_api: bool = _bool("TELEMETRY_ENABLE_API", True)
    enable_agent: bool = _bool("TELEMETRY_ENABLE_AGENT", True)
    enable_rag: bool = _bool("TELEMETRY_ENABLE_RAG", True)
    enable_llm: bool = _bool("TELEMETRY_ENABLE_LLM", True)
    enable_business: bool = _bool("TELEMETRY_ENABLE_BUSINESS", True)
    enable_security: bool = _bool("TELEMETRY_ENABLE_SECURITY", True)
    log_prompts: bool = _bool("TELEMETRY_LOG_PROMPTS", False)
    log_responses: bool = _bool("TELEMETRY_LOG_RESPONSES", False)
    log_pii: bool = _bool("TELEMETRY_LOG_PII", False)
    token_cost_input_per_1k: float = float(os.getenv("TOKEN_COST_INPUT_PER_1K", "0.0000"))
    token_cost_output_per_1k: float = float(os.getenv("TOKEN_COST_OUTPUT_PER_1K", "0.0000"))
    currency: str = os.getenv("CURRENCY", "USD")

    @property
    def application_insights_configured(self) -> bool:
        return bool(self.applicationinsights_connection_string or self.applicationinsights_instrumentation_key)

    def safe_summary(self) -> dict:
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "application_insights": "configured" if self.application_insights_configured else "missing",
            "log_level": self.log_level,
            "log_format": self.log_format,
            "service_name": self.service_name,
            "environment": self.environment,
            "sample_rate": self.sample_rate,
            "enable_api": self.enable_api,
            "enable_agent": self.enable_agent,
            "enable_rag": self.enable_rag,
            "enable_llm": self.enable_llm,
            "enable_business": self.enable_business,
            "enable_security": self.enable_security,
            "log_prompts": self.log_prompts,
            "log_responses": self.log_responses,
            "log_pii": self.log_pii,
            "currency": self.currency,
        }


observability_config = ObservabilityConfig()
