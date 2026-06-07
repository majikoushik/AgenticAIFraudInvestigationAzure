export type CostSummary = {
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  estimated_total_cost: number;
  currency: string;
  total_cases_with_cost: number;
  average_cost_per_case: number;
  average_tokens_per_case: number;
  highest_cost_case_id?: string | null;
  highest_cost_agent?: string | null;
  pricing_configured: boolean;
};

export type TokenUsageRecord = {
  usage_id: string;
  case_id?: string | null;
  agent_name: string;
  operation_name: string;
  ai_provider: string;
  model_or_deployment: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  retry_count: number;
  fallback_used: boolean;
  success: boolean;
  created_at: string;
};

export type TokenUsageSummary = {
  count: number;
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  by_provider: Record<string, number>;
  by_model: Record<string, number>;
  records: TokenUsageRecord[];
};

export type CostGroup = {
  name: string;
  agent_name?: string;
  model_or_deployment?: string;
  provider?: string;
  total_tokens: number;
  estimated_cost: number;
  call_count: number;
  average_tokens_per_call: number;
  average_cost_per_call: number;
};

export type DailyCostTrend = {
  days: number;
  trend: Array<{ date: string; estimated_cost: number; total_tokens: number; call_count: number }>;
};

export type BudgetStatus = {
  daily_budget_limit: number;
  daily_estimated_cost: number;
  daily_budget_used_percentage: number;
  monthly_budget_limit: number;
  monthly_estimated_cost: number;
  monthly_budget_used_percentage: number;
  token_daily_limit: number;
  daily_tokens_used: number;
  daily_token_limit_used_percentage: number;
  status: "OK" | "WARNING" | "EXCEEDED" | "NOT_CONFIGURED";
  case_thresholds: { status: string; threshold: number; exceeded_cases: Array<{ case_id: string; estimated_cost: number }> };
};

export type CostAnomaly = {
  anomaly_detected: boolean;
  anomaly_type: string;
  current_value: number;
  baseline_value: number;
  increase_percentage: number;
  threshold_percentage: number;
  status: "ANOMALY" | "NORMAL" | "NOT_ENOUGH_DATA";
};

export type CaseCostBreakdown = {
  case_id: string;
  case_status?: string | null;
  ai_recommendation?: string | null;
  human_decision?: string | null;
  human_override: boolean;
  total_tokens: number;
  estimated_total_cost: number;
  currency: string;
};
