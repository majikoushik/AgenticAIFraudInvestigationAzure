import { apiClient } from "@/services/apiClient";
import type { Incident, IncidentListResponse } from "@/types/incident.types";

export function getIncidents(): Promise<IncidentListResponse> {
  return apiClient<IncidentListResponse>("/api/v1/incidents");
}

export function getIncident(incidentId: string): Promise<Incident> {
  return apiClient<Incident>(`/api/v1/incidents/${incidentId}`);
}

export function updateIncidentStatus(incidentId: string, targetStatus: string, actor = "local.ops", comment?: string): Promise<Incident> {
  return apiClient<Incident>(`/api/v1/incidents/${incidentId}/status`, { method: "PATCH", body: JSON.stringify({ target_status: targetStatus, actor, comment }) });
}

export function assignIncident(incidentId: string, assignedTo: string, actor = "local.ops", comment?: string): Promise<Incident> {
  return apiClient<Incident>(`/api/v1/incidents/${incidentId}/assign`, { method: "PATCH", body: JSON.stringify({ assigned_to: assignedTo, actor, comment }) });
}

export function addIncidentTimeline(incidentId: string, action: string, comment: string, actor = "local.ops"): Promise<Incident> {
  return apiClient<Incident>(`/api/v1/incidents/${incidentId}/timeline`, { method: "POST", body: JSON.stringify({ actor, action, comment }) });
}
