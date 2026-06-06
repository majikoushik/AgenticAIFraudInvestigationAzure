type CaseStatusBadgeProps = {
  status: string;
};

export function CaseStatusBadge({ status }: CaseStatusBadgeProps) {
  const classNameByStatus: Record<string, string> = {
    NEW: "status-new",
    AI_INVESTIGATION_IN_PROGRESS: "status-progress",
    AI_INVESTIGATION_COMPLETED: "status-completed",
    PENDING_HUMAN_REVIEW: "status-review",
    APPROVED: "status-approved",
    HELD: "status-held",
    ESCALATED: "status-escalated",
    REJECTED: "status-rejected",
    CLOSED: "status-closed"
  };
  const className = classNameByStatus[status] ?? "status-badge";
  return <span className={`badge ${className}`}>{status}</span>;
}
