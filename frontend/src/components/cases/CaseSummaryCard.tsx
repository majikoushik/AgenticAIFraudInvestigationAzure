import { CardFrame } from "@/components/cases/CardFrame";
import { CaseStatusBadge } from "@/components/cases/CaseStatusBadge";
import { MetaList } from "@/components/cases/MetaList";
import type { CaseDetail } from "@/types/case.types";
import { formatDateTime, normalizeRiskClass } from "@/utils/maskingUtils";

type CaseSummaryCardProps = {
  caseDetail: CaseDetail;
};

export function CaseSummaryCard({ caseDetail }: CaseSummaryCardProps) {
  return (
    <CardFrame title="Case Summary" subtitle="Alert metadata and current workflow state.">
      <div className="stack">
        <span className={`badge ${normalizeRiskClass(caseDetail.metadata.severity)}`}>{caseDetail.metadata.severity}</span>
        <CaseStatusBadge status={caseDetail.current_status} />
        <MetaList
          rows={[
            { label: "Alert ID", value: caseDetail.metadata.alert_id },
            { label: "Status", value: caseDetail.current_status },
            { label: "AI Recommendation", value: caseDetail.ai_recommendation ?? "Not available" },
            { label: "Created", value: formatDateTime(caseDetail.metadata.created_at) },
            { label: "Reason", value: caseDetail.metadata.reason }
          ]}
        />
      </div>
    </CardFrame>
  );
}
