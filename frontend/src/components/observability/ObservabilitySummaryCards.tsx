import type { HealthDetails } from "@/types/observability.types";

export function ObservabilitySummaryCards({ details }: { details: HealthDetails }) {
  const checks = details.checks;
  return (
    <div className="stats-grid grid full-span">
      <div className="stat-card card"><p className="stat-label">Health</p><p className="stat-value">{details.status}</p></div>
      <div className="stat-card card"><p className="stat-label">Telemetry</p><p className="stat-value">{checks.telemetry}</p></div>
      <div className="stat-card card"><p className="stat-label">App Insights</p><p className="stat-value">{checks.application_insights}</p></div>
      <div className="stat-card card"><p className="stat-label">Azure OpenAI</p><p className="stat-value">{checks.azure_openai_config}</p></div>
      <div className="stat-card card"><p className="stat-label">Azure Search</p><p className="stat-value">{checks.azure_search_config}</p></div>
    </div>
  );
}
