import { apiClient } from "./apiClient";
import type {
  ReadinessAssessment,
  ReadinessCategoryResult,
  ReadinessCheckDefinition,
  ReadinessEvidence,
  ReadinessEvidencePayload,
  ReadinessReportResult,
  ReadinessRiskCreatePayload,
  ReadinessRiskItem,
  ReadinessRiskUpdatePayload,
  GoLiveDecisionResponse,
  RunAssessmentPayload,
} from "@/types/readiness.types";

const BASE = "/api/v1/readiness";

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
export async function getReadinessHealth(): Promise<{ status: string; config: Record<string, unknown> }> {
  return apiClient(`${BASE}/config/health`);
}

// ---------------------------------------------------------------------------
// Checklist
// ---------------------------------------------------------------------------
export async function getChecklist(
  category?: string
): Promise<{ total: number; categories: string[]; checklist: Record<string, ReadinessCheckDefinition[]> }> {
  const qs = category ? `?category=${encodeURIComponent(category)}` : "";
  return apiClient(`${BASE}/checklist${qs}`);
}

// ---------------------------------------------------------------------------
// Assessments
// ---------------------------------------------------------------------------
export async function runAssessment(
  payload: RunAssessmentPayload
): Promise<ReadinessAssessment> {
  return apiClient(`${BASE}/assessments/run`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function listAssessments(opts?: {
  environment?: string;
  limit?: number;
}): Promise<{ count: number; assessments: ReadinessAssessment[] }> {
  const params = new URLSearchParams();
  if (opts?.environment) params.set("environment", opts.environment);
  if (opts?.limit) params.set("limit", String(opts.limit));
  const qs = params.toString() ? `?${params}` : "";
  return apiClient(`${BASE}/assessments${qs}`);
}

export async function getAssessment(
  assessmentId: string
): Promise<ReadinessAssessment> {
  return apiClient(`${BASE}/assessments/${assessmentId}`);
}

export async function getCategoryResult(
  assessmentId: string,
  category: string
): Promise<ReadinessCategoryResult> {
  return apiClient(`${BASE}/assessments/${assessmentId}/category/${category}`);
}

export async function getGoLiveDecision(
  assessmentId: string
): Promise<GoLiveDecisionResponse> {
  return apiClient(`${BASE}/assessments/${assessmentId}/go-live-decision`);
}

// ---------------------------------------------------------------------------
// Evidence
// ---------------------------------------------------------------------------
export async function addEvidence(
  assessmentId: string,
  payload: ReadinessEvidencePayload
): Promise<ReadinessEvidence> {
  return apiClient(`${BASE}/assessments/${assessmentId}/evidence`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// ---------------------------------------------------------------------------
// Export
// ---------------------------------------------------------------------------
export async function exportAssessment(
  assessmentId: string,
  format: "markdown" | "json" = "markdown"
): Promise<ReadinessReportResult> {
  return apiClient(
    `${BASE}/assessments/${assessmentId}/export?format=${format}`,
    { method: "POST", body: JSON.stringify({}) }
  );
}

// ---------------------------------------------------------------------------
// Risk Register
// ---------------------------------------------------------------------------
export async function listRisks(opts?: {
  status?: string;
  category?: string;
  severity?: string;
}): Promise<{ count: number; risks: ReadinessRiskItem[] }> {
  const params = new URLSearchParams();
  if (opts?.status) params.set("status", opts.status);
  if (opts?.category) params.set("category", opts.category);
  if (opts?.severity) params.set("severity", opts.severity);
  const qs = params.toString() ? `?${params}` : "";
  return apiClient(`${BASE}/risks${qs}`);
}

export async function createRisk(
  payload: ReadinessRiskCreatePayload
): Promise<ReadinessRiskItem> {
  return apiClient(`${BASE}/risks`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateRisk(
  riskId: string,
  payload: ReadinessRiskUpdatePayload
): Promise<ReadinessRiskItem> {
  return apiClient(`${BASE}/risks/${riskId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function closeRisk(
  riskId: string,
  comment?: string
): Promise<ReadinessRiskItem> {
  return apiClient(`${BASE}/risks/${riskId}/close`, {
    method: "POST",
    body: JSON.stringify({ comment }),
  });
}
