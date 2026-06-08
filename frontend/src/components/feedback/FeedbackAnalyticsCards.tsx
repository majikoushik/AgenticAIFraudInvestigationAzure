import type { FeedbackAnalyticsResponse } from "@/types/feedback.types";

export function FeedbackAnalyticsCards({ analytics }: { analytics: FeedbackAnalyticsResponse }) {
  const cards = [
    ["Total Feedback", analytics.summary.total_feedback],
    ["Negative Rate", `${analytics.summary.negative_feedback_rate_percentage ?? 0}%`],
    ["Critical Feedback", analytics.summary.critical_feedback_count],
    ["Open Backlog", analytics.summary.open_backlog_count],
    ["Wrong Citations", analytics.rag_quality.wrong_policy_citation_count as number],
    ["Incorrect Recommendations", analytics.recommendation_quality.incorrect_recommendation_count as number]
  ];
  return (
    <div className="metric-grid">
      {cards.map(([label, value]) => <div className="metric-card" key={label}><span>{label}</span><strong>{value}</strong></div>)}
    </div>
  );
}
