import type { BudgetStatus } from "@/types/cost.types";
import { formatCost, formatPercent, formatTokens } from "@/components/cost/costFormat";

export function BudgetStatusPanel({ budget, currency }: { budget: BudgetStatus; currency: string }) {
  return (
    <section className="panel">
      <h2>Budget Status</h2>
      <div className="status-line"><strong>{budget.status}</strong></div>
      <div className="stack">
        <div className="row"><span>Daily budget</span><strong>{formatCost(budget.daily_estimated_cost, currency, 4)} / {formatCost(budget.daily_budget_limit, currency, 2)}</strong></div>
        <div className="row"><span>Daily used</span><strong>{formatPercent(budget.daily_budget_used_percentage)}</strong></div>
        <div className="row"><span>Monthly budget</span><strong>{formatCost(budget.monthly_estimated_cost, currency, 4)} / {formatCost(budget.monthly_budget_limit, currency, 2)}</strong></div>
        <div className="row"><span>Monthly used</span><strong>{formatPercent(budget.monthly_budget_used_percentage)}</strong></div>
        <div className="row"><span>Daily tokens</span><strong>{formatTokens(budget.daily_tokens_used)} / {formatTokens(budget.token_daily_limit)}</strong></div>
      </div>
    </section>
  );
}
