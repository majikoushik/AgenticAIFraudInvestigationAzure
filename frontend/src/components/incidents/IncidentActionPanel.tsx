"use client";

import { useState } from "react";
import { addIncidentTimeline, assignIncident, updateIncidentStatus } from "@/services/incidentService";
import type { Incident } from "@/types/incident.types";

export function IncidentActionPanel({ incident, onUpdated }: { incident: Incident; onUpdated: (incident: Incident) => void }) {
  const [assignedTo, setAssignedTo] = useState(incident.assigned_to);
  async function setStatus(status: string) { onUpdated(await updateIncidentStatus(incident.incident_id, status, "local.ops", `Moving to ${status}.`)); }
  async function assign() { onUpdated(await assignIncident(incident.incident_id, assignedTo, "local.ops", "Assignment updated.")); }
  async function note() { onUpdated(await addIncidentTimeline(incident.incident_id, "INVESTIGATION_NOTE", "Checked local telemetry and runbook.", "local.ops")); }
  return (
    <div className="card"><div className="card-body stack">
      <button className="button" onClick={() => setStatus("ACKNOWLEDGED")}>Acknowledge</button>
      <button className="button" onClick={() => setStatus("INVESTIGATING")}>Investigating</button>
      <button className="button" onClick={() => setStatus("MITIGATED")}>Mitigated</button>
      <button className="button" onClick={() => setStatus("RESOLVED")}>Resolved</button>
      <button className="button" onClick={() => setStatus("CLOSED")}>Closed</button>
      <input value={assignedTo} onChange={(event) => setAssignedTo(event.target.value)} />
      <button className="button secondary" onClick={assign}>Assign</button>
      <button className="button secondary" onClick={note}>Add Timeline Note</button>
    </div></div>
  );
}
