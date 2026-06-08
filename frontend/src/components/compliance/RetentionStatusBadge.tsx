export function RetentionStatusBadge({ value }: { value: string }) {
  return <span className={`status-pill ${value.includes("PURGE") ? "risk-high" : value.includes("ARCHIVE") ? "risk-medium" : "risk-low"}`}>{value}</span>;
}
