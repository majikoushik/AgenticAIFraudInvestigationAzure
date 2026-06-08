import type { AssignmentPriority } from "@/types/assignment.types";

export function AssignmentPriorityBadge({ priority }: { priority: AssignmentPriority | string }) {
  return <span className={`badge priority-${String(priority).toLowerCase()}`}>{priority}</span>;
}
