import type { AssignmentHistoryRecord } from "@/types/assignment.types";
import { formatDateTime } from "@/utils/maskingUtils";

export function AssignmentHistoryPanel({ history }: { history: AssignmentHistoryRecord[] }) {
  return (
    <section className="card">
      <div className="card-header">
        <h3>Assignment History</h3>
        <p>Ownership changes for this case.</p>
      </div>
      <div className="card-body timeline">
        {history.length === 0 ? (
          <div className="empty-state">No assignment history yet.</div>
        ) : history.map((item) => (
          <div className="timeline-item" key={item.history_id}>
            <h4>{item.action}</h4>
            <p>{item.previous_assigned_to ?? "Unassigned"} to {item.new_assigned_to ?? "Unassigned"}</p>
            <p>{item.actor} ({item.actor_role}) at {formatDateTime(item.timestamp)}</p>
            {item.comment && <p>{item.comment}</p>}
          </div>
        ))}
      </div>
    </section>
  );
}
