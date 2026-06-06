import { CardFrame } from "@/components/cases/CardFrame";
import { CaseStatusBadge } from "@/components/cases/CaseStatusBadge";
import { MetaList } from "@/components/cases/MetaList";
import type { CaseStatusInfo } from "@/types/status.types";
import { formatDateTime } from "@/utils/maskingUtils";

type StatusLifecyclePanelProps = {
  statusInfo: CaseStatusInfo | null;
};

export function StatusLifecyclePanel({ statusInfo }: StatusLifecyclePanelProps) {
  if (!statusInfo) {
    return (
      <CardFrame title="Status Lifecycle" subtitle="Current case state and allowed transitions.">
        <div className="empty-state">Status lifecycle details are not available.</div>
      </CardFrame>
    );
  }

  return (
    <CardFrame title="Status Lifecycle" subtitle="Backend-enforced state machine for this case.">
      <div className="stack">
        <CaseStatusBadge status={statusInfo.status} />
        <MetaList
          rows={[
            { label: "Allowed Next Statuses", value: statusInfo.allowed_next_statuses.join(", ") || "None" },
            { label: "Last Updated By", value: statusInfo.status_updated_by ?? "Not available" },
            {
              label: "Last Updated At",
              value: statusInfo.status_updated_at ? formatDateTime(statusInfo.status_updated_at) : "Not available"
            },
            { label: "Status Comment", value: statusInfo.status_comment ?? "Not available" }
          ]}
        />
      </div>
    </CardFrame>
  );
}
