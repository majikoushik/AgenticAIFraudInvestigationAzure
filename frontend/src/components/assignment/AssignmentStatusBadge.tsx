import type { AssignmentStatus } from "@/types/assignment.types";

export function AssignmentStatusBadge({ status }: { status: AssignmentStatus | string }) {
  return <span className={`badge assignment-${String(status).toLowerCase()}`}>{status}</span>;
}
