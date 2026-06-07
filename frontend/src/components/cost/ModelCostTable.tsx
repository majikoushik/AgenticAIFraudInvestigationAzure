import type { CostGroup } from "@/types/cost.types";
import { formatCost, formatTokens } from "@/components/cost/costFormat";

export function ModelCostTable({ models, currency }: { models: CostGroup[]; currency: string }) {
  return (
    <section className="panel">
      <h2>Model Cost</h2>
      <div className="table-wrap"><table><thead><tr><th>Model</th><th>Provider</th><th>Tokens</th><th>Estimated cost</th><th>Calls</th></tr></thead>
        <tbody>{models.map((model) => <tr key={model.name}><td>{model.name}</td><td>{model.provider ?? "unknown"}</td><td>{formatTokens(model.total_tokens)}</td><td>{formatCost(model.estimated_cost, currency)}</td><td>{model.call_count}</td></tr>)}</tbody>
      </table></div>
    </section>
  );
}
