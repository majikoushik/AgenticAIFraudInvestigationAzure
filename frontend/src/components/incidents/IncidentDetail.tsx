import { AlertSeverityBadge } from "@/components/alerts/AlertSeverityBadge";
import { IncidentStatusBadge } from "@/components/incidents/IncidentStatusBadge";
import { IncidentTimeline } from "@/components/incidents/IncidentTimeline";
import type { Incident } from "@/types/incident.types";

export function IncidentDetail({ incident }: { incident: Incident }) {
  return (
    <div className="card"><div className="card-body stack">
      <h3>{incident.title}</h3>
      <p>{incident.description}</p>
      <div className="meta-row"><span className="meta-label">Severity</span><AlertSeverityBadge severity={incident.severity} /></div>
      <div className="meta-row"><span className="meta-label">Status</span><IncidentStatusBadge status={incident.status} /></div>
      <div className="meta-row"><span className="meta-label">Assigned to</span><span className="meta-value">{incident.assigned_to}</span></div>
      <div className="meta-row"><span className="meta-label">Alert</span><span className="meta-value">{incident.alert_id}</span></div>
      <div className="meta-row"><span className="meta-label">Runbook</span><span className="meta-value">{incident.runbook}</span></div>
      <h4>Timeline</h4>
      <IncidentTimeline timeline={incident.timeline} />
    </div></div>
  );
}
