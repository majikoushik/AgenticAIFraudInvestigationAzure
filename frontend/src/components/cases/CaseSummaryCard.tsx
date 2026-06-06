import { CardFrame } from "@/components/cases/CardFrame";
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
        <MetaList
          rows={[
            { label: "Alert ID", value: caseDetail.metadata.alert_id },
            { label: "Status", value: caseDetail.current_status },
            { label: "Created", value: formatDateTime(caseDetail.metadata.created_at) },
            { label: "Reason", value: caseDetail.metadata.reason }
          ]}
        />
      </div>
    </CardFrame>
  );
}
