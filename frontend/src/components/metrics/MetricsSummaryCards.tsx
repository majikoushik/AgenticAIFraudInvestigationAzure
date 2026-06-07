import { MetricCard } from "@/components/metrics/MetricCard";
import { formatDuration, formatPercent } from "@/components/metrics/metricsFormat";
import type { MetricsSummary } from "@/types/metrics.types";

type MetricsSummaryCardsProps = {
  metrics: MetricsSummary;
};

export function MetricsSummaryCards({ metrics }: MetricsSummaryCardsProps) {
  return (
    <div className="metrics-summary-grid">
      <MetricCard label="Total Cases" value={metrics.case_status_metrics.total_cases} />
      <MetricCard label="Pending Human Review" value={metrics.case_status_metrics.pending_human_review_cases} tone="warning" />
      <MetricCard label="Override Rate" value={formatPercent(metrics.human_override_metrics.override_rate_percentage)} tone="danger" />
      <MetricCard label="AI-Human Match Rate" value={formatPercent(metrics.human_override_metrics.ai_human_match_rate_percentage)} tone="success" />
      <MetricCard label="Avg Investigation Time" value={formatDuration(metrics.investigation_time_metrics.average_ai_investigation_duration_seconds)} />
      <MetricCard label="Agent Failure Rate" value={formatPercent(metrics.agent_execution_metrics.agent_failure_rate_percentage)} tone="warning" />
    </div>
  );
}
