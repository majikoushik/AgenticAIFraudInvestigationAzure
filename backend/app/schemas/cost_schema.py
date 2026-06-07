from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.token_usage_schema import TokenUsageRecord


class CostRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    cost_id: str
    usage_id: str
    case_id: str | None = None
    agent_name: str
    operation_name: str
    ai_provider: str
    model_or_deployment: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    input_token_cost_per_1k: float = 0.0
    output_token_cost_per_1k: float = 0.0
    estimated_input_cost: float = 0.0
    estimated_output_cost: float = 0.0
    estimated_total_cost: float = 0.0
    currency: str = "USD"
    cost_source: str = "estimated_local"
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CostSummaryResponse(BaseModel):
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    estimated_total_cost: float
    currency: str
    total_cases_with_cost: int
    average_cost_per_case: float
    average_tokens_per_case: float
    highest_cost_case_id: str | None = None
    highest_cost_agent: str | None = None
    pricing_configured: bool


class TokenUsageSummaryResponse(BaseModel):
    count: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    by_provider: dict[str, int] = Field(default_factory=dict)
    by_model: dict[str, int] = Field(default_factory=dict)
    records: list[TokenUsageRecord] = Field(default_factory=list)


class CaseCostBreakdownResponse(BaseModel):
    case_id: str
    case_status: str | None = None
    ai_recommendation: str | None = None
    human_decision: str | None = None
    human_override: bool = False
    total_tokens: int
    estimated_total_cost: float
    currency: str
    agent_breakdown: list[dict[str, Any]] = Field(default_factory=list)
    token_usage_records: list[TokenUsageRecord] = Field(default_factory=list)
    cost_records: list[CostRecord] = Field(default_factory=list)


class AgentCostBreakdownResponse(BaseModel):
    agents: list[dict[str, Any]]


class ModelCostBreakdownResponse(BaseModel):
    models: list[dict[str, Any]]


class DailyCostTrendResponse(BaseModel):
    days: int
    trend: list[dict[str, Any]]


class BudgetStatusResponse(BaseModel):
    daily_budget_limit: float
    daily_estimated_cost: float
    daily_budget_used_percentage: float
    monthly_budget_limit: float
    monthly_estimated_cost: float
    monthly_budget_used_percentage: float
    token_daily_limit: int
    daily_tokens_used: int
    daily_token_limit_used_percentage: float
    status: str
    case_thresholds: dict[str, Any] = Field(default_factory=dict)


class CostAnomalyResponse(BaseModel):
    anomalies: list[dict[str, Any]]
