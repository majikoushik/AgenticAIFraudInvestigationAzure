import type { CaseCostBreakdown } from "@/types/cost.types";
import { formatCost, formatTokens } from "@/components/cost/costFormat";

export function CaseCostBreakdownPanel({ item, currency }: { item?: CaseCostBreakdown; currency: string }) {
  if (!item) return null;
  return (
    <section className="panel">
      <h2>Case Cost</h2>
      <div className="row"><span>{item.case_id}</span><strong>{formatCost(item.estimated_total_cost, currency)} / {formatTokens(item.total_tokens)} tokens</strong></div>
    </section>
  );
}
