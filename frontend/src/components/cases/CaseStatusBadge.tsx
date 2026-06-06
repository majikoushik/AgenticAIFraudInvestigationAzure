type CaseStatusBadgeProps = {
  status: string;
};

export function CaseStatusBadge({ status }: CaseStatusBadgeProps) {
  const className = status === "PENDING_HUMAN_REVIEW" ? "risk-medium" : status === "CLOSED" ? "risk-low" : "status-badge";
  return <span className={`badge ${className}`}>{status}</span>;
}
