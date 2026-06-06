import { apiClient } from "@/services/apiClient";
import type { AuditEventListResponse, AuditEventTypeInfo, AuditSearchFilters, AuditTrail } from "@/types/audit.types";

export function getAuditTrail(caseId: string): Promise<AuditTrail> {
  return apiClient<AuditTrail>(`/api/v1/cases/${caseId}/audit`);
}

export function getCaseAuditTrail(caseId: string): Promise<AuditTrail> {
  return getAuditTrail(caseId);
}

export function searchAuditEvents(filters: AuditSearchFilters): Promise<AuditEventListResponse> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });
  return apiClient<AuditEventListResponse>(`/api/v1/audit/search?${params.toString()}`);
}

export function getAuditEventTypes(): Promise<{ event_types: AuditEventTypeInfo[] }> {
  return apiClient<{ event_types: AuditEventTypeInfo[] }>("/api/v1/audit/event-types");
}
