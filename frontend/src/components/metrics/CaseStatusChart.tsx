import { CardFrame } from "@/components/cases/CardFrame";
import { entries, formatPercent } from "@/components/metrics/metricsFormat";
import type { CaseStatusMetrics } from "@/types/metrics.types";

type CaseStatusChartProps = {
  metrics: CaseStatusMetrics;
};

export function CaseStatusChart({ metrics }: CaseStatusChartProps) {
  const rows = entries(metrics.status_counts);

  return (
    <CardFrame title="Case Status" subtitle="Current case lifecycle distribution.">
      {rows.length === 0 ? (
        <div className="empty-state">No case status metrics available.</div>
      ) : (
        <div className="metric-bars">
          {rows.map(([status, count]) => {
            const percent = metrics.status_percentages[status] ?? 0;
            return (
              <div className="metric-bar-row" key={status}>
                <div className="metric-bar-label">
                  <span>{status}</span>
                  <strong>{count} | {formatPercent(percent)}</strong>
                </div>
                <div className="metric-bar-track">
                  <div className="metric-bar-fill" style={{ width: `${Math.min(percent, 100)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </CardFrame>
  );
}
