export function LegalHoldBadge({ value }: { value: string }) {
  return <span className={`status-pill ${value === "ACTIVE" ? "risk-high" : "risk-low"}`}>{value}</span>;
}
