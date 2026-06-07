type MetricCardProps = {
  label: string;
  value: string | number;
  detail?: string;
  tone?: "default" | "success" | "warning" | "danger";
};

export function MetricCard({ label, value, detail, tone = "default" }: MetricCardProps) {
  return (
    <div className={`metric-card metric-card-${tone}`}>
      <p className="stat-label">{label}</p>
      <p className="stat-value">{value}</p>
      {detail && <p className="metric-detail">{detail}</p>}
    </div>
  );
}
