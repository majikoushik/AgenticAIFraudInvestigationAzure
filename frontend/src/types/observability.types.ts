export type HealthDetails = {
  status: "ok" | "degraded" | "unhealthy";
  checks: Record<string, string>;
  observability: Record<string, string | boolean | number>;
};

export type TelemetryEvent = {
  timestamp: string;
  telemetry_type: string;
  name: string;
  properties: Record<string, unknown>;
  measurements: Record<string, number>;
};
