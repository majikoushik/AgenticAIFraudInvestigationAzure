import { apiClient } from "@/services/apiClient";
import type { LegalHold } from "@/types/legalHold.types";

export function getLegalHolds(): Promise<LegalHold[]> {
  return apiClient<LegalHold[]>("/api/v1/legal-holds");
}

export function createLegalHold(payload: Record<string, unknown>): Promise<LegalHold> {
  return apiClient<LegalHold>("/api/v1/legal-holds", { method: "POST", body: JSON.stringify(payload) });
}

export function releaseLegalHold(legalHoldId: string, releaseReason: string): Promise<LegalHold> {
  return apiClient<LegalHold>(`/api/v1/legal-holds/${legalHoldId}/release`, { method: "POST", body: JSON.stringify({ release_reason: releaseReason }) });
}
