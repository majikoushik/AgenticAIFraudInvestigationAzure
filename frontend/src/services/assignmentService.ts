import { apiClient } from "@/services/apiClient";
import type {
  AssignmentHistoryResponse,
  AssignmentPriority,
  AssignmentResponse,
  QueueFilters,
  QueueResponse,
  WorkloadSummary
} from "@/types/assignment.types";

function query(filters?: QueueFilters): string {
  const params = new URLSearchParams();
  Object.entries(filters ?? {}).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  const value = params.toString();
  return value ? `?${value}` : "";
}

export function getMyQueue(filters?: QueueFilters): Promise<QueueResponse> {
  return apiClient<QueueResponse>(`/api/v1/queues/my${query(filters)}`);
}

export function getUnassignedQueue(filters?: QueueFilters): Promise<QueueResponse> {
  return apiClient<QueueResponse>(`/api/v1/queues/unassigned${query(filters)}`);
}

export function getTeamQueue(filters?: QueueFilters): Promise<QueueResponse> {
  return apiClient<QueueResponse>(`/api/v1/queues/team${query(filters)}`);
}

export function getEscalatedQueue(filters?: QueueFilters): Promise<QueueResponse> {
  return apiClient<QueueResponse>(`/api/v1/queues/escalated${query(filters)}`);
}

export function getSlaRiskQueue(filters?: QueueFilters): Promise<QueueResponse> {
  return apiClient<QueueResponse>(`/api/v1/queues/sla-risk${query(filters)}`);
}

export function assignCase(caseId: string, payload: {
  assigned_to: string;
  assigned_to_name: string;
  assigned_to_role: string;
  assigned_team: string;
  assignment_priority: AssignmentPriority;
  sla_due_at?: string | null;
  comment?: string | null;
}): Promise<AssignmentResponse> {
  return apiClient<AssignmentResponse>(`/api/v1/cases/${caseId}/assign`, { method: "POST", body: JSON.stringify(payload) });
}

export function reassignCase(caseId: string, payload: Parameters<typeof assignCase>[1]): Promise<AssignmentResponse> {
  return apiClient<AssignmentResponse>(`/api/v1/cases/${caseId}/reassign`, { method: "POST", body: JSON.stringify(payload) });
}

export function acceptCase(caseId: string, acceptedBy: string, comment?: string): Promise<AssignmentResponse> {
  return apiClient<AssignmentResponse>(`/api/v1/cases/${caseId}/accept`, { method: "POST", body: JSON.stringify({ accepted_by: acceptedBy, comment }) });
}

export function releaseCase(caseId: string, releasedBy: string, reason: string, comment?: string): Promise<AssignmentResponse> {
  return apiClient<AssignmentResponse>(`/api/v1/cases/${caseId}/release`, { method: "POST", body: JSON.stringify({ released_by: releasedBy, reason, comment }) });
}

export function transferCase(caseId: string, payload: Omit<Parameters<typeof assignCase>[1], "assignment_priority">): Promise<AssignmentResponse> {
  return apiClient<AssignmentResponse>(`/api/v1/cases/${caseId}/transfer`, { method: "POST", body: JSON.stringify(payload) });
}

export function getAssignmentHistory(caseId: string): Promise<AssignmentHistoryResponse> {
  return apiClient<AssignmentHistoryResponse>(`/api/v1/cases/${caseId}/assignment-history`);
}

export function getWorkloadSummary(): Promise<WorkloadSummary> {
  return apiClient<WorkloadSummary>("/api/v1/assignment/workload");
}

export function refreshSlaStatus(): Promise<{ message: string; updated_count: number }> {
  return apiClient<{ message: string; updated_count: number }>("/api/v1/assignment/sla/refresh", { method: "POST" });
}
