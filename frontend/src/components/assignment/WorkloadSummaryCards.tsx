import type { WorkloadSummary } from "@/types/assignment.types";

export function WorkloadSummaryCards({ summary }: { summary: WorkloadSummary }) {
  return (
    <div className="metrics-summary-grid">
      <div className="metric-card"><p className="stat-label">Assigned</p><p className="stat-value">{summary.total_assigned_cases}</p></div>
      <div className="metric-card"><p className="stat-label">Unassigned</p><p className="stat-value">{summary.total_unassigned_cases}</p></div>
      <div className="metric-card"><p className="stat-label">Avg Load</p><p className="stat-value">{summary.average_cases_per_investigator}</p></div>
      <div className="metric-card metric-card-warning"><p className="stat-label">At Risk</p><p className="stat-value">{summary.cases_by_sla_status.AT_RISK ?? 0}</p></div>
      <div className="metric-card metric-card-danger"><p className="stat-label">Breached</p><p className="stat-value">{summary.cases_by_sla_status.BREACHED ?? 0}</p></div>
      <div className="metric-card"><p className="stat-label">Overloaded</p><p className="stat-value">{summary.overloaded_investigators.length}</p></div>
    </div>
  );
}
