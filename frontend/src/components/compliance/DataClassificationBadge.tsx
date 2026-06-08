export function DataClassificationBadge({ value }: { value: string }) {
  return <span className={`status-pill ${value === "RESTRICTED" ? "risk-high" : value === "CONFIDENTIAL" ? "risk-medium" : "risk-low"}`}>{value}</span>;
}
