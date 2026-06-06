import { apiClient } from "@/services/apiClient";
import type { CaseDetail, CaseListRow, CaseSummary } from "@/types/case.types";
import { formatCurrency, maskCustomerId } from "@/utils/maskingUtils";

export function getCaseSummaries(): Promise<CaseSummary[]> {
  return apiClient<CaseSummary[]>("/api/v1/cases");
}

export function getCaseDetail(caseId: string): Promise<CaseDetail> {
  return apiClient<CaseDetail>(`/api/v1/cases/${caseId}`);
}

export async function getCaseRows(): Promise<CaseListRow[]> {
  const summaries = await getCaseSummaries();
  const details = await Promise.all(summaries.map((item) => getCaseDetail(item.case_id)));

  return details.map((detail) => ({
    case_id: detail.metadata.case_id,
    customer_label: detail.customer.display_name || maskCustomerId(detail.customer.customer_id),
    transaction_amount: formatCurrency(
      detail.suspicious_transaction.amount,
      detail.suspicious_transaction.currency
    ),
    alert_type: detail.metadata.reason,
    risk_level: detail.metadata.severity,
    status: detail.current_status,
    created_at: detail.metadata.created_at
  }));
}
