import { apiClient } from "@/services/apiClient";
import type { ComplianceExport, ComplianceSummary } from "@/types/compliance.types";

export function getComplianceSummary(): Promise<ComplianceSummary> {
  return apiClient<ComplianceSummary>("/api/v1/compliance/summary");
}

export function getRetentionSummary(): Promise<ComplianceSummary> {
  return apiClient<ComplianceSummary>("/api/v1/compliance/retention-summary");
}

export function createCaseComplianceExport(caseId: string, payload: Record<string, unknown>): Promise<ComplianceExport> {
  return apiClient<ComplianceExport>(`/api/v1/compliance/exports/case/${caseId}`, { method: "POST", body: JSON.stringify(payload) });
}

export function getComplianceExports(): Promise<ComplianceExport[]> {
  return apiClient<ComplianceExport[]>("/api/v1/compliance/exports");
}
