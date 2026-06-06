import { apiClient } from "@/services/apiClient";
import type { AuditTrail } from "@/types/audit.types";

export function getAuditTrail(caseId: string): Promise<AuditTrail> {
  return apiClient<AuditTrail>(`/api/v1/cases/${caseId}/audit`);
}
