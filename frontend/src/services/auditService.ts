import { apiClient } from "@/services/apiClient";
import type { AuditTrail } from "@/types/audit.types";
import type { DecisionRequest, DecisionResponse } from "@/types/decision.types";

export function getAuditTrail(caseId: string): Promise<AuditTrail> {
  return apiClient<AuditTrail>(`/api/v1/cases/${caseId}/audit`);
}

export function submitDecision(caseId: string, decision: DecisionRequest): Promise<DecisionResponse> {
  return apiClient<DecisionResponse>(`/api/v1/cases/${caseId}/decision`, {
    method: "POST",
    body: JSON.stringify(decision)
  });
}
