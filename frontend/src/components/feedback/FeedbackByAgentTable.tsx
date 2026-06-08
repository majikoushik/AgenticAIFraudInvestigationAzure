import type { FeedbackAnalyticsResponse } from "@/types/feedback.types";

export function FeedbackByAgentTable({ analytics }: { analytics: FeedbackAnalyticsResponse }) {
  return (
    <section className="card">
      <div className="card-header"><h3>Feedback By Agent</h3><p>Problem areas by agent output.</p></div>
      <div className="card-body">
        <table className="data-table"><thead><tr><th>Agent</th><th>Feedback</th></tr></thead><tbody>
          {Object.entries(analytics.by_agent).map(([agent, count]) => <tr key={agent}><td>{agent}</td><td>{count}</td></tr>)}
        </tbody></table>
      </div>
    </section>
  );
}
