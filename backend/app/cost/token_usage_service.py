from datetime import datetime, timezone
from math import ceil
from uuid import uuid4

from app.cost.cost_estimator import CostEstimator
from app.cost.cost_repository import CostRepository
from app.observability import telemetry_events
from app.observability.pii_safe_logging import sanitize_telemetry_properties
from app.observability.telemetry_client import get_telemetry_client


class TokenUsageService:
    def __init__(self, repository: CostRepository | None = None, estimator: CostEstimator | None = None) -> None:
        self.repository = repository or CostRepository()
        self.estimator = estimator or CostEstimator()

    def record_token_usage(
        self,
        case_id: str | None,
        agent_name: str,
        operation_name: str,
        ai_provider: str,
        model_or_deployment: str,
        prompt_tokens: int | None,
        completion_tokens: int | None,
        metadata: dict | None = None,
        success: bool = True,
        error_type: str | None = None,
        correlation_id: str | None = None,
    ) -> dict:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        prompt = max(int(prompt_tokens or 0), 0)
        completion = max(int(completion_tokens or 0), 0)
        record = {
            "usage_id": f"TOK-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "case_id": case_id,
            "correlation_id": correlation_id,
            "agent_name": agent_name,
            "operation_name": operation_name,
            "ai_provider": ai_provider,
            "model_or_deployment": model_or_deployment,
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": prompt + completion,
            "input_char_count": int((metadata or {}).get("input_char_count", 0) or 0),
            "output_char_count": int((metadata or {}).get("output_char_count", 0) or 0),
            "rag_context_tokens_estimate": int((metadata or {}).get("rag_context_tokens_estimate", 0) or 0),
            "retrieval_source_count": int((metadata or {}).get("retrieval_source_count", 0) or 0),
            "retry_count": int((metadata or {}).get("retry_count", 0) or 0),
            "fallback_used": bool((metadata or {}).get("fallback_used", False)),
            "success": success,
            "error_type": error_type,
            "created_at": now,
            "metadata": sanitize_telemetry_properties(metadata or {}),
        }
        self.repository.append_token_usage_record(record)
        cost = self.estimator.estimate_total_cost_for_usage(record)
        cost_record = {
            "cost_id": f"COST-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}",
            "usage_id": record["usage_id"],
            "case_id": case_id,
            "agent_name": agent_name,
            "operation_name": operation_name,
            "ai_provider": ai_provider,
            "model_or_deployment": model_or_deployment,
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": prompt + completion,
            "input_token_cost_per_1k": cost["input_token_cost_per_1k"],
            "output_token_cost_per_1k": cost["output_token_cost_per_1k"],
            "estimated_input_cost": cost["estimated_input_cost"],
            "estimated_output_cost": cost["estimated_output_cost"],
            "estimated_total_cost": cost["estimated_total_cost"],
            "currency": cost["currency"],
            "cost_source": "estimated_local",
            "created_at": now,
            "metadata": {"pricing_configured": cost["pricing_configured"]},
        }
        self.repository.append_cost_record(cost_record)
        self._emit_telemetry(record, cost_record)
        return {"token_usage_record": record, "cost_record": cost_record}

    @staticmethod
    def estimate_tokens_from_text(text: str) -> int:
        return ceil(len(text or "") / 4)

    def summarize_token_usage(self, filters: dict | None = None) -> dict:
        filters = filters or {}
        records = self.repository.search_records(**filters)["token_usage_records"]
        return {
            "count": len(records),
            "prompt_tokens": sum(record.get("prompt_tokens", 0) for record in records),
            "completion_tokens": sum(record.get("completion_tokens", 0) for record in records),
            "total_tokens": sum(record.get("total_tokens", 0) for record in records),
            "records": records,
        }

    @staticmethod
    def _emit_telemetry(usage: dict, cost: dict) -> None:
        try:
            properties = {
                "case_id": usage.get("case_id"),
                "agent_name": usage.get("agent_name"),
                "provider": usage.get("ai_provider"),
                "model_or_deployment": usage.get("model_or_deployment"),
                "pricing_configured": cost.get("metadata", {}).get("pricing_configured"),
                "currency": cost.get("currency"),
            }
            measurements = {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "estimated_cost": cost.get("estimated_total_cost", 0),
            }
            get_telemetry_client().track_event(telemetry_events.TOKEN_USAGE_RECORDED, properties, measurements)
            get_telemetry_client().track_event(telemetry_events.COST_ESTIMATED, properties, measurements)
        except Exception:
            return None
