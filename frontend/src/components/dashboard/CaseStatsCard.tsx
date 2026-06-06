type CaseStatsCardProps = {
  label: string;
  value: number;
  tone?: "low" | "medium" | "high";
};

export function CaseStatsCard({ label, value, tone = "low" }: CaseStatsCardProps) {
  return (
    <article className="card stat-card">
      <p className="stat-label">{label}</p>
      <p className={`stat-value ${tone === "high" ? "risk-high" : tone === "medium" ? "risk-medium" : ""}`}>
        {value}
      </p>
    </article>
  );
}
