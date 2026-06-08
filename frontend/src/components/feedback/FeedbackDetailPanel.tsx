import type { FeedbackRecord } from "@/types/feedback.types";

export function FeedbackDetailPanel({ feedback }: { feedback: FeedbackRecord | null }) {
  if (!feedback) return <div className="empty-state">Select feedback to view details.</div>;
  return (
    <section className="card">
      <div className="card-header"><h3>{feedback.feedback_id}</h3><p>{feedback.target_type}</p></div>
      <div className="card-body meta-list">
        <div className="meta-row"><span className="meta-label">Rating</span><span className="meta-value">{feedback.rating}</span></div>
        <div className="meta-row"><span className="meta-label">Issues</span><span className="meta-value">{feedback.issue_types.join(", ") || "None"}</span></div>
        <div className="meta-row"><span className="meta-label">Comment</span><span className="meta-value">{feedback.comment || "No comment"}</span></div>
      </div>
    </section>
  );
}
