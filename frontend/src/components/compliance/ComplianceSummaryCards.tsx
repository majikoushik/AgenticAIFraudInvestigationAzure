import type { ComplianceSummary } from "@/types/compliance.types";

export function ComplianceSummaryCards({ summary }: { summary: ComplianceSummary | null }) {
  const items = [
    ["Archive Candidates", summary?.archive_candidates ?? 0],
    ["Purge Candidates", summary?.purge_candidates ?? 0],
    ["Legal Holds", summary?.legal_hold_count ?? 0],
    ["Review Required", summary?.review_required_count ?? 0],
    ["Exports", summary?.exports_generated ?? 0],
    ["Policies", summary?.policy_count ?? 0]
  ];
  return (
    <section className="metrics-grid">
      {items.map(([label, value]) => (
        <article className="metric-card" key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </article>
      ))}
    </section>
  );
}
