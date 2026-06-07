import { CardFrame } from "@/components/cases/CardFrame";
import { entries, formatPercent } from "@/components/metrics/metricsFormat";
import type { AgentExecutionMetrics } from "@/types/metrics.types";

type AgentMetricsPanelProps = {
  metrics: AgentExecutionMetrics;
};

export function AgentMetricsPanel({ metrics }: AgentMetricsPanelProps) {
  return (
    <CardFrame title="Agent Execution" subtitle="Agent success, failure, and duration telemetry from audit events.">
      <div className="facts-grid">
        <div><span className="label">Executions</span><strong>{metrics.total_agent_executions}</strong></div>
        <div><span className="label">Success</span><strong>{metrics.agent_success_count}</strong></div>
        <div><span className="label">Failures</span><strong>{metrics.agent_failure_count}</strong></div>
        <div><span className="label">Failure rate</span><strong>{formatPercent(metrics.agent_failure_rate_percentage)}</strong></div>
      </div>
      <MetricTable title="Executions by agent" values={metrics.execution_count_by_agent} durationValues={metrics.average_duration_by_agent} />
      <MetricTable title="Failures by agent" values={metrics.failure_count_by_agent} />
    </CardFrame>
  );
}

function MetricTable({ title, values, durationValues }: { title: string; values: Record<string, number>; durationValues?: Record<string, number> }) {
  const rows = entries(values);
  return (
    <div>
      <h4>{title}</h4>
      {rows.length === 0 ? <div className="empty-state">No agent metrics available.</div> : (
        <table className="table">
          <thead><tr><th>Agent</th><th>Count</th>{durationValues && <th>Avg duration</th>}</tr></thead>
          <tbody>
            {rows.map(([agent, count]) => (
              <tr key={agent}><td>{agent}</td><td>{count}</td>{durationValues && <td>{durationValues[agent] ? `${durationValues[agent].toFixed(1)}ms` : "n/a"}</td>}</tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
