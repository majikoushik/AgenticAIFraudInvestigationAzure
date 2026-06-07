import Link from "next/link";
import { AlertSeverityBadge } from "@/components/alerts/AlertSeverityBadge";
import { IncidentStatusBadge } from "@/components/incidents/IncidentStatusBadge";
import type { Incident } from "@/types/incident.types";

export function IncidentList({ incidents }: { incidents: Incident[] }) {
  if (incidents.length === 0) return <div className="empty-state">No incidents found.</div>;
  return (
    <div className="table-wrap card full-span">
      <table><thead><tr><th>Severity</th><th>Status</th><th>Title</th><th>Assigned</th><th>Created</th></tr></thead>
      <tbody>{incidents.map((incident) => (
        <tr key={incident.incident_id}>
          <td><AlertSeverityBadge severity={incident.severity} /></td>
          <td><IncidentStatusBadge status={incident.status} /></td>
          <td><Link href={`/incidents/${incident.incident_id}`}>{incident.title}</Link></td>
          <td>{incident.assigned_to}</td><td>{incident.created_at}</td>
        </tr>
      ))}</tbody></table>
    </div>
  );
}
