import type { FeedbackRecord } from "@/types/feedback.types";

export function FeedbackList({ records }: { records: FeedbackRecord[] }) {
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead><tr><th>ID</th><th>Case</th><th>Target</th><th>Rating</th><th>Severity</th><th>Disposition</th><th>Submitted</th></tr></thead>
        <tbody>
          {records.map((item) => (
            <tr key={item.feedback_id}>
              <td>{item.feedback_id}</td>
              <td>{item.case_id}</td>
              <td>{item.target_type}</td>
              <td>{item.rating}</td>
              <td>{item.severity}</td>
              <td>{item.disposition}</td>
              <td>{new Date(item.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
