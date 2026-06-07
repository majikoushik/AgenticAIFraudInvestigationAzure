export type IncidentTimelineEvent = {
  timestamp: string;
  actor: string;
  action: string;
  comment: string;
};

export type Incident = {
  incident_id: string;
  alert_id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  assigned_to: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  runbook?: string;
  timeline: IncidentTimelineEvent[];
};

export type IncidentListResponse = {
  count: number;
  incidents: Incident[];
};
