import { apiClient } from "@/services/apiClient";
import type { BudgetStatus, CaseCostBreakdown, CostAnomaly, CostGroup, CostSummary, DailyCostTrend, TokenUsageSummary } from "@/types/cost.types";

export function getCostHealth(): Promise<{ pricing_configured: boolean; currency: string; mode: string }> {
  return apiClient("/api/v1/cost/health");
}

export function getCostSummary(): Promise<CostSummary> {
  return apiClient("/api/v1/cost/summary");
}

export function getTokenUsage(): Promise<TokenUsageSummary> {
  return apiClient("/api/v1/cost/token-usage");
}

export function getDailyCostTrend(days = 30): Promise<DailyCostTrend> {
  return apiClient(`/api/v1/cost/trends/daily?days=${days}`);
}

export function getAgentCosts(): Promise<{ agents: CostGroup[] }> {
  return apiClient("/api/v1/cost/agents");
}

export function getModelCosts(): Promise<{ models: CostGroup[] }> {
  return apiClient("/api/v1/cost/models");
}

export function getTopCases(): Promise<{ cases: CaseCostBreakdown[] }> {
  return apiClient("/api/v1/cost/top-cases");
}

export function getBudgetStatus(): Promise<BudgetStatus> {
  return apiClient("/api/v1/cost/budget/status");
}

export function getCostAnomalies(): Promise<{ anomalies: CostAnomaly[] }> {
  return apiClient("/api/v1/cost/anomalies");
}

export async function getCostDashboard() {
  const [health, summary, tokenUsage, trend, agents, models, topCases, budget, anomalies] = await Promise.all([
    getCostHealth(),
    getCostSummary(),
    getTokenUsage(),
    getDailyCostTrend(),
    getAgentCosts(),
    getModelCosts(),
    getTopCases(),
    getBudgetStatus(),
    getCostAnomalies()
  ]);
  return { health, summary, tokenUsage, trend, agents: agents.agents, models: models.models, topCases: topCases.cases, budget, anomalies: anomalies.anomalies };
}
