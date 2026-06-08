"use client";

import { updateBacklogStatus } from "@/services/feedbackService";
import type { FeedbackBacklogItem } from "@/types/feedback.types";

export function FeedbackBacklogTable({ items, onUpdated }: { items: FeedbackBacklogItem[]; onUpdated?: () => void }) {
  async function close(backlogId: string) {
    await updateBacklogStatus(backlogId, "CLOSED");
    onUpdated?.();
  }
  return (
    <div className="table-wrap">
      <table className="data-table">
        <thead><tr><th>Backlog ID</th><th>Feedback</th><th>Type</th><th>Title</th><th>Priority</th><th>Status</th><th>Owner</th><th>Created</th><th>Action</th></tr></thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.backlog_id}>
              <td>{item.backlog_id}</td>
              <td>{item.feedback_id}</td>
              <td>{item.backlog_type}</td>
              <td>{item.title}</td>
              <td>{item.priority}</td>
              <td>{item.status}</td>
              <td>{item.owner}</td>
              <td>{new Date(item.created_at).toLocaleString()}</td>
              <td><button className="button secondary" onClick={() => close(item.backlog_id)}>Close</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
