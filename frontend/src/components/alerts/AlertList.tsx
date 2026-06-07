import { AlertSeverityBadge } from "@/components/alerts/AlertSeverityBadge";
import { AlertTypeBadge } from "@/components/alerts/AlertTypeBadge";
import type { AlertEvent } from "@/types/alert.types";

export function AlertList({ alerts }: { alerts: AlertEvent[] }) {
  if (alerts.length === 0) return <div className="empty-state">No alerts found.</div>;
  return (
    <div className="table-wrap card full-span">
      <table><thead><tr><th>Severity</th><th>Type</th><th>Title</th><th>Status</th><th>Created</th></tr></thead>
      <tbody>{alerts.map((alert) => (
        <tr key={alert.alert_id}>
          <td><AlertSeverityBadge severity={alert.severity} /></td>
          <td><AlertTypeBadge alertType={alert.alert_type} /></td>
          <td>{alert.title}</td><td>{alert.status}</td><td>{alert.created_at}</td>
        </tr>
      ))}</tbody></table>
    </div>
  );
}
