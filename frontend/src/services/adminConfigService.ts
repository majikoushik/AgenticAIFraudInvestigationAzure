import { apiClient } from "@/services/apiClient";
import type { AdminConfigCategory, AdminConfigHistoryRecord, AdminConfigResponse, AdminConfigUpdateRequest, AdminConfigUpdateResponse, ConfigHealthResponse, FeatureFlag } from "@/types/adminConfig.types";

export function getAdminConfig(): Promise<AdminConfigResponse> {
  return apiClient("/api/v1/admin/config");
}

export function getAdminConfigCategory(category: string): Promise<AdminConfigCategory> {
  return apiClient(`/api/v1/admin/config/${category}`);
}

export function updateAdminConfig(payload: AdminConfigUpdateRequest): Promise<AdminConfigUpdateResponse> {
  return apiClient("/api/v1/admin/config", { method: "PATCH", body: JSON.stringify(payload) });
}

export function resetAdminConfig(comment: string): Promise<{ reset_count: number; message: string }> {
  return apiClient("/api/v1/admin/config/reset", { method: "POST", body: JSON.stringify({ comment }) });
}

export function getAdminConfigHistory(): Promise<AdminConfigHistoryRecord[]> {
  return apiClient("/api/v1/admin/config/history");
}

export function getAdminConfigHealth(): Promise<ConfigHealthResponse> {
  return apiClient("/api/v1/admin/config/health");
}

export function getFeatureFlags(): Promise<FeatureFlag[]> {
  return apiClient("/api/v1/admin/feature-flags");
}

export function updateFeatureFlag(flagKey: string, enabled: boolean, comment?: string): Promise<FeatureFlag> {
  return apiClient(`/api/v1/admin/feature-flags/${flagKey}`, { method: "PATCH", body: JSON.stringify({ enabled, comment }) });
}

export async function getAdminConfigDashboard() {
  const [config, health, history, featureFlags] = await Promise.all([getAdminConfig(), getAdminConfigHealth(), getAdminConfigHistory(), getFeatureFlags()]);
  return { config, health, history, featureFlags };
}
