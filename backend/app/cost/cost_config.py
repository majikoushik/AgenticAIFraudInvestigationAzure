import os
from dataclasses import dataclass, field


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() == "true"


def _float(name: str, default: str = "0.0000") -> float:
    try:
        return float(os.getenv(name, default))
    except ValueError:
        return float(default)


def _int(name: str, default: str = "0") -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return int(default)


@dataclass(frozen=True)
class CostMonitoringConfig:
    enabled: bool = field(default_factory=lambda: _bool("COST_MONITORING_ENABLED", True))
    mode: str = field(default_factory=lambda: os.getenv("COST_MONITORING_MODE", "local"))
    cost_local_store_path: str = field(default_factory=lambda: os.getenv("COST_LOCAL_STORE_PATH", "data/synthetic/cost_records.json"))
    currency: str = field(default_factory=lambda: os.getenv("CURRENCY", "USD"))
    default_input_token_cost_per_1k: float = field(default_factory=lambda: _float("DEFAULT_INPUT_TOKEN_COST_PER_1K"))
    default_output_token_cost_per_1k: float = field(default_factory=lambda: _float("DEFAULT_OUTPUT_TOKEN_COST_PER_1K"))
    gpt4o_mini_input_cost_per_1k: float = field(default_factory=lambda: _float("AZURE_OPENAI_GPT4O_MINI_INPUT_COST_PER_1K"))
    gpt4o_mini_output_cost_per_1k: float = field(default_factory=lambda: _float("AZURE_OPENAI_GPT4O_MINI_OUTPUT_COST_PER_1K"))
    gpt4o_input_cost_per_1k: float = field(default_factory=lambda: _float("AZURE_OPENAI_GPT4O_INPUT_COST_PER_1K"))
    gpt4o_output_cost_per_1k: float = field(default_factory=lambda: _float("AZURE_OPENAI_GPT4O_OUTPUT_COST_PER_1K"))
    embedding_input_cost_per_1k: float = field(default_factory=lambda: _float("AZURE_OPENAI_EMBEDDING_INPUT_COST_PER_1K"))
    daily_budget_limit: float = field(default_factory=lambda: _float("COST_DAILY_BUDGET_LIMIT", "50"))
    monthly_budget_limit: float = field(default_factory=lambda: _float("COST_MONTHLY_BUDGET_LIMIT", "1000"))
    token_daily_limit: int = field(default_factory=lambda: _int("TOKEN_DAILY_LIMIT", "1000000"))
    token_per_case_warning_threshold: int = field(default_factory=lambda: _int("TOKEN_PER_CASE_WARNING_THRESHOLD", "25000"))
    cost_per_case_warning_threshold: float = field(default_factory=lambda: _float("COST_PER_CASE_WARNING_THRESHOLD", "2.00"))
    anomaly_percent_increase_threshold: float = field(default_factory=lambda: _float("COST_ANOMALY_PERCENT_INCREASE_THRESHOLD", "50"))
    anomaly_min_baseline_days: int = field(default_factory=lambda: _int("COST_ANOMALY_MIN_BASELINE_DAYS", "3"))
    azure_cost_management_enabled: bool = field(default_factory=lambda: _bool("AZURE_COST_MANAGEMENT_ENABLED", False))
    azure_subscription_id: str = field(default_factory=lambda: os.getenv("AZURE_SUBSCRIPTION_ID", ""))
    azure_resource_group_name: str = field(default_factory=lambda: os.getenv("AZURE_RESOURCE_GROUP_NAME", ""))
    azure_openai_resource_name: str = field(default_factory=lambda: os.getenv("AZURE_OPENAI_RESOURCE_NAME", ""))
    azure_ai_search_resource_name: str = field(default_factory=lambda: os.getenv("AZURE_AI_SEARCH_RESOURCE_NAME", ""))

    @property
    def model_specific_rates(self) -> dict[str, dict[str, float]]:
        return {
            "gpt-4o-mini": {"input": self.gpt4o_mini_input_cost_per_1k, "output": self.gpt4o_mini_output_cost_per_1k},
            "gpt-4o": {"input": self.gpt4o_input_cost_per_1k, "output": self.gpt4o_output_cost_per_1k},
            "text-embedding": {"input": self.embedding_input_cost_per_1k, "output": 0.0},
            "embedding": {"input": self.embedding_input_cost_per_1k, "output": 0.0},
        }

    def get_rate_for_model(self, model_or_deployment: str) -> dict[str, float | bool]:
        model = (model_or_deployment or "").lower()
        rate = None
        for key, value in self.model_specific_rates.items():
            if key in model:
                rate = value
                break
        if rate is None:
            rate = {"input": self.default_input_token_cost_per_1k, "output": self.default_output_token_cost_per_1k}
        return {
            "input_token_cost_per_1k": rate["input"],
            "output_token_cost_per_1k": rate["output"],
            "pricing_configured": bool(rate["input"] or rate["output"]),
        }

    def safe_summary(self) -> dict:
        return {
            "cost_monitoring_enabled": self.enabled,
            "mode": self.mode,
            "currency": self.currency,
            "pricing_configured": any(
                [
                    self.default_input_token_cost_per_1k,
                    self.default_output_token_cost_per_1k,
                    self.gpt4o_mini_input_cost_per_1k,
                    self.gpt4o_mini_output_cost_per_1k,
                    self.gpt4o_input_cost_per_1k,
                    self.gpt4o_output_cost_per_1k,
                    self.embedding_input_cost_per_1k,
                ]
            ),
            "daily_budget_limit": self.daily_budget_limit,
            "monthly_budget_limit": self.monthly_budget_limit,
            "token_daily_limit": self.token_daily_limit,
            "token_per_case_warning_threshold": self.token_per_case_warning_threshold,
            "cost_per_case_warning_threshold": self.cost_per_case_warning_threshold,
            "azure_cost_management_enabled": self.azure_cost_management_enabled,
            "azure_subscription_configured": bool(self.azure_subscription_id),
            "azure_resource_group_configured": bool(self.azure_resource_group_name),
        }


cost_monitoring_config = CostMonitoringConfig()
