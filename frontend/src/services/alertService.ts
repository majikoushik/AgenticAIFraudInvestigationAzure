import { apiClient } from "@/services/apiClient";
import type { AlertEvent, AlertListResponse } from "@/types/alert.types";

export function getAlerts(): Promise<AlertListResponse> {
  return apiClient<AlertListResponse>("/api/v1/alerts");
}

export function getAlert(alertId: string): Promise<AlertEvent> {
  return apiClient<AlertEvent>(`/api/v1/alerts/${alertId}`);
}

export function evaluateAlerts(): Promise<{ evaluated_rules: number; alerts_created: number; alerts: AlertEvent[] }> {
  return apiClient("/api/v1/alerts/evaluate", { method: "POST" });
}

export function simulateAlert(payload: { alert_type: string; severity: string; title: string; description: string }): Promise<{ alert: AlertEvent; incident?: unknown }> {
  return apiClient("/api/v1/alerts/simulate", { method: "POST", body: JSON.stringify(payload) });
}
