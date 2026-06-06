import { apiClient } from "@/services/apiClient";
import type { CaseStatusInfo } from "@/types/status.types";

export function getCaseStatus(caseId: string): Promise<CaseStatusInfo> {
  return apiClient<CaseStatusInfo>(`/api/v1/cases/${caseId}/status`);
}
