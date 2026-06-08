import type { FeedbackAnalyticsResponse } from "@/types/feedback.types";

export function FeedbackTrendPanel({ analytics }: { analytics: FeedbackAnalyticsResponse }) {
  const trend = analytics.trends.feedback_by_day ?? {};
  return (
    <section className="card">
      <div className="card-header"><h3>Feedback Trend</h3><p>Daily feedback volume.</p></div>
      <div className="card-body">
        <table className="data-table"><thead><tr><th>Date</th><th>Feedback</th></tr></thead><tbody>
          {Object.entries(trend).map(([day, count]) => <tr key={day}><td>{day}</td><td>{count}</td></tr>)}
        </tbody></table>
      </div>
    </section>
  );
}
