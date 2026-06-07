import { apiClient } from "@/services/apiClient";
import type { HealthDetails, TelemetryEvent } from "@/types/observability.types";

export function getHealthDetails(): Promise<HealthDetails> {
  return apiClient<HealthDetails>("/api/v1/health/details");
}

export function getRecentTelemetryEvents(): Promise<TelemetryEvent[]> {
  return apiClient<TelemetryEvent[]>("/api/v1/observability/events");
}
