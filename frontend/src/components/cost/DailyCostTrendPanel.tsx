import type { DailyCostTrend } from "@/types/cost.types";
import { formatCost, formatTokens } from "@/components/cost/costFormat";

export function DailyCostTrendPanel({ trend, currency }: { trend: DailyCostTrend; currency: string }) {
  const maxTokens = Math.max(...trend.trend.map((item) => item.total_tokens), 1);
  return (
    <section className="panel span-2">
      <h2>Daily Cost Trend</h2>
      {trend.trend.length === 0 ? <div className="empty-state">No daily trend records yet.</div> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Date</th><th>Tokens</th><th>Estimated cost</th><th>Calls</th><th>Volume</th></tr></thead>
            <tbody>
              {trend.trend.map((item) => (
                <tr key={item.date}>
                  <td>{item.date}</td>
                  <td>{formatTokens(item.total_tokens)}</td>
                  <td>{formatCost(item.estimated_cost, currency)}</td>
                  <td>{item.call_count}</td>
                  <td><div className="bar"><span style={{ width: `${Math.max((item.total_tokens / maxTokens) * 100, 4)}%` }} /></div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
