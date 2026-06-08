import { apiClient } from "@/services/apiClient";
import type { DataCategory, RetentionPolicy, RetentionScanResult } from "@/types/retention.types";

export function getRetentionPolicies(): Promise<RetentionPolicy[]> {
  return apiClient<RetentionPolicy[]>("/api/v1/retention/policies");
}

export function updateRetentionPolicy(dataCategory: DataCategory, payload: Partial<RetentionPolicy>): Promise<RetentionPolicy> {
  return apiClient<RetentionPolicy>(`/api/v1/retention/policies/${dataCategory}`, { method: "PATCH", body: JSON.stringify(payload) });
}

export function runRetentionScan(payload: { data_category?: DataCategory; dry_run: boolean }): Promise<RetentionScanResult> {
  return apiClient<RetentionScanResult>("/api/v1/retention/scan", { method: "POST", body: JSON.stringify(payload) });
}

export function getRetentionReviewQueue(): Promise<{ count: number; candidates: RetentionScanResult["candidates"] }> {
  return apiClient<{ count: number; candidates: RetentionScanResult["candidates"] }>("/api/v1/retention/review-queue");
}

export function archiveRetentionCandidates(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  return apiClient<Record<string, unknown>>("/api/v1/retention/archive", { method: "POST", body: JSON.stringify(payload) });
}

export function purgeRetentionCandidates(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  return apiClient<Record<string, unknown>>("/api/v1/retention/purge", { method: "POST", body: JSON.stringify(payload) });
}
