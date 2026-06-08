import type { SlaStatus } from "@/types/assignment.types";

export function SlaStatusBadge({ status }: { status: SlaStatus | string }) {
  return <span className={`badge sla-${String(status).toLowerCase().replace("_", "-")}`}>{status}</span>;
}
