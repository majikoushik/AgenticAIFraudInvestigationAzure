from app.cost.cost_config import CostMonitoringConfig, cost_monitoring_config


class CostEstimator:
    def __init__(self, config: CostMonitoringConfig | None = None) -> None:
        self.config = config or cost_monitoring_config

    def estimate_llm_cost(self, model_or_deployment: str, prompt_tokens: int | None, completion_tokens: int | None) -> dict:
        prompt = max(int(prompt_tokens or 0), 0)
        completion = max(int(completion_tokens or 0), 0)
        rates = self.config.get_rate_for_model(model_or_deployment)
        input_rate = float(rates["input_token_cost_per_1k"])
        output_rate = float(rates["output_token_cost_per_1k"])
        input_cost = round((prompt / 1000) * input_rate, 6)
        output_cost = round((completion / 1000) * output_rate, 6)
        total = round(input_cost + output_cost, 6)
        return {
            "input_token_cost_per_1k": input_rate,
            "output_token_cost_per_1k": output_rate,
            "estimated_input_cost": input_cost,
            "estimated_output_cost": output_cost,
            "estimated_total_cost": total,
            "currency": self.config.currency,
            "pricing_configured": bool(rates["pricing_configured"]),
            "warning": None if rates["pricing_configured"] else "Pricing values are not configured; estimated cost is 0.",
        }

    def estimate_embedding_cost(self, model_or_deployment: str, input_tokens: int | None) -> dict:
        return self.estimate_llm_cost(model_or_deployment, input_tokens, 0)

    def estimate_total_cost_for_usage(self, token_usage_record: dict) -> dict:
        return self.estimate_llm_cost(
            token_usage_record.get("model_or_deployment", ""),
            token_usage_record.get("prompt_tokens", 0),
            token_usage_record.get("completion_tokens", 0),
        )
