import Link from "next/link";
import type { CaseListRow } from "@/types/case.types";
import { formatDateTime, normalizeRiskClass } from "@/utils/maskingUtils";

type CaseListProps = {
  cases: CaseListRow[];
};

export function CaseList({ cases }: CaseListProps) {
  return (
    <section className="card">
      <div className="card-header">
        <h3>Fraud Case Queue</h3>
        <p>Prioritized synthetic fraud cases ready for investigator review.</p>
      </div>
      <div className="table-wrap">
        {cases.length === 0 ? (
          <div className="empty-state">No cases found.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Customer</th>
                <th>Transaction Amount</th>
                <th>Alert Type</th>
                <th>Risk Level</th>
                <th>Status</th>
                <th>Created Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((item) => (
                <tr key={item.case_id}>
                  <td>{item.case_id}</td>
                  <td>{item.customer_label}</td>
                  <td>{item.transaction_amount}</td>
                  <td>{item.alert_type}</td>
                  <td>
                    <span className={`badge ${normalizeRiskClass(item.risk_level)}`}>{item.risk_level}</span>
                  </td>
                  <td>
                    <span className="badge status-badge">{item.status}</span>
                  </td>
                  <td>{formatDateTime(item.created_at)}</td>
                  <td>
                    <Link className="button secondary" href={`/cases/${item.case_id}`}>
                      View Case
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
