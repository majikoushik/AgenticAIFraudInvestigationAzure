import { apiClient } from "@/services/apiClient";
import type { InvestigationPackage } from "@/types/agent.types";

export function runInvestigation(caseId: string): Promise<InvestigationPackage> {
  return apiClient<InvestigationPackage>(`/api/v1/cases/${caseId}/investigate`, {
    method: "POST"
  });
}
