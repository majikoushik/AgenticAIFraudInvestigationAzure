import type { CostGroup } from "@/types/cost.types";
import { formatCost, formatTokens } from "@/components/cost/costFormat";

export function AgentCostTable({ agents, currency }: { agents: CostGroup[]; currency: string }) {
  return (
    <section className="panel">
      <h2>Agent Cost</h2>
      <div className="table-wrap"><table><thead><tr><th>Agent</th><th>Tokens</th><th>Estimated cost</th><th>Calls</th><th>Avg tokens</th><th>Avg cost</th></tr></thead>
        <tbody>{agents.map((agent) => <tr key={agent.name}><td>{agent.name}</td><td>{formatTokens(agent.total_tokens)}</td><td>{formatCost(agent.estimated_cost, currency)}</td><td>{agent.call_count}</td><td>{formatTokens(agent.average_tokens_per_call)}</td><td>{formatCost(agent.average_cost_per_call, currency)}</td></tr>)}</tbody>
      </table></div>
    </section>
  );
}
