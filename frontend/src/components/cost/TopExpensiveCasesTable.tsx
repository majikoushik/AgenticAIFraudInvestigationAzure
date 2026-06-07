import type { CaseCostBreakdown } from "@/types/cost.types";
import { formatCost, formatTokens } from "@/components/cost/costFormat";

export function TopExpensiveCasesTable({ cases, currency }: { cases: CaseCostBreakdown[]; currency: string }) {
  return (
    <section className="panel span-2">
      <h2>Top Expensive Cases</h2>
      <div className="table-wrap"><table><thead><tr><th>Case</th><th>Tokens</th><th>Estimated cost</th><th>Status</th><th>AI rec</th><th>Human decision</th><th>Override</th></tr></thead>
        <tbody>{cases.map((item) => <tr key={item.case_id}><td>{item.case_id}</td><td>{formatTokens(item.total_tokens)}</td><td>{formatCost(item.estimated_total_cost, currency)}</td><td>{item.case_status ?? "Unknown"}</td><td>{item.ai_recommendation ?? "-"}</td><td>{item.human_decision ?? "-"}</td><td>{item.human_override ? "Yes" : "No"}</td></tr>)}</tbody>
      </table></div>
    </section>
  );
}
