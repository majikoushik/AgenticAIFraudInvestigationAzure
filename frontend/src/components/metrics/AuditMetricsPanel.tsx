import { CardFrame } from "@/components/cases/CardFrame";
import { entries } from "@/components/metrics/metricsFormat";
import type { AuditMetrics } from "@/types/metrics.types";
import { formatDateTime } from "@/utils/maskingUtils";

type AuditMetricsPanelProps = {
  metrics: AuditMetrics;
};

export function AuditMetricsPanel({ metrics }: AuditMetricsPanelProps) {
  return (
    <CardFrame title="Audit Metrics" subtitle="Audit event volume and distribution.">
      <div className="facts-grid">
        <div><span className="label">Total audit events</span><strong>{metrics.total_audit_events}</strong></div>
        <div><span className="label">Latest event</span><strong>{metrics.latest_audit_event_timestamp ? formatDateTime(metrics.latest_audit_event_timestamp) : "n/a"}</strong></div>
      </div>
      <div className="three-column-panel">
        <AuditList title="By category" values={metrics.audit_events_by_category} />
        <AuditList title="By type" values={metrics.audit_events_by_type} />
        <AuditList title="By actor role" values={metrics.audit_events_by_actor_role} />
      </div>
    </CardFrame>
  );
}

function AuditList({ title, values }: { title: string; values: Record<string, number> }) {
  const rows = entries(values);
  return (
    <div>
      <h4>{title}</h4>
      {rows.length === 0 ? <div className="empty-state">No audit events.</div> : (
        <table className="table">
          <thead><tr><th>Value</th><th>Count</th></tr></thead>
          <tbody>{rows.map(([name, count]) => <tr key={name}><td>{name}</td><td>{count}</td></tr>)}</tbody>
        </table>
      )}
    </div>
  );
}
