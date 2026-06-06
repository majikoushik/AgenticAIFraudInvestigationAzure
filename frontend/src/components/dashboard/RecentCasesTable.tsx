import Link from "next/link";
import type { CaseSummary } from "@/types/case.types";
import { formatDateTime, maskCustomerId, normalizeRiskClass } from "@/utils/maskingUtils";

type RecentCasesTableProps = {
  cases: CaseSummary[];
};

export function RecentCasesTable({ cases }: RecentCasesTableProps) {
  return (
    <section className="card">
      <div className="card-header">
        <h3>Recent Fraud Cases</h3>
        <p>Latest synthetic alerts from the backend case API.</p>
      </div>
      <div className="table-wrap">
        {cases.length === 0 ? (
          <div className="empty-state">No fraud cases available.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Customer</th>
                <th>Risk</th>
                <th>Status</th>
                <th>Created</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((item) => (
                <tr key={item.case_id}>
                  <td>{item.case_id}</td>
                  <td>{maskCustomerId(item.customer_id)}</td>
                  <td>
                    <span className={`badge ${normalizeRiskClass(item.severity)}`}>{item.severity}</span>
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
