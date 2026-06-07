import type { CostSummary } from "@/types/cost.types";
import { formatCost, formatTokens } from "@/components/cost/costFormat";

export function CostSummaryCards({ summary }: { summary: CostSummary }) {
  const cards = [
    ["Total Tokens", formatTokens(summary.total_tokens)],
    ["Estimated Total Cost", formatCost(summary.estimated_total_cost, summary.currency)],
    ["Average Cost per Case", formatCost(summary.average_cost_per_case, summary.currency)],
    ["Average Tokens per Case", formatTokens(summary.average_tokens_per_case)],
    ["Highest Cost Agent", summary.highest_cost_agent ?? "None"],
    ["Pricing", summary.pricing_configured ? "Configured" : "Not configured"]
  ];
  return (
    <section className="panel span-2">
      <div className="metric-card-grid">
        {cards.map(([label, value]) => (
          <div className="metric-card" key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
