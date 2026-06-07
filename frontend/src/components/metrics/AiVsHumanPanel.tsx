import { CardFrame } from "@/components/cases/CardFrame";
import { entries, formatPercent } from "@/components/metrics/metricsFormat";
import type { AIRecommendationMetrics, HumanDecisionMetrics, HumanOverrideMetrics } from "@/types/metrics.types";

type AiVsHumanPanelProps = {
  aiMetrics: AIRecommendationMetrics;
  decisionMetrics: HumanDecisionMetrics;
  overrideMetrics: HumanOverrideMetrics;
};

export function AiVsHumanPanel({ aiMetrics, decisionMetrics, overrideMetrics }: AiVsHumanPanelProps) {
  return (
    <CardFrame title="AI vs Human Decisions" subtitle="Recommendation acceptance, review decisions, and override rate.">
      <div className="two-column-panel">
        <Distribution title="AI Recommendations" values={aiMetrics.recommendation_counts} percentages={aiMetrics.recommendation_percentages} />
        <Distribution title="Human Decisions" values={decisionMetrics.decision_counts} percentages={decisionMetrics.decision_percentages} />
      </div>
      <div className="facts-grid">
        <div><span className="label">Match count</span><strong>{overrideMetrics.ai_human_match_count}</strong></div>
        <div><span className="label">Override count</span><strong>{overrideMetrics.total_overrides}</strong></div>
        <div><span className="label">Override rate</span><strong>{formatPercent(overrideMetrics.override_rate_percentage)}</strong></div>
        <div><span className="label">Missing AI recommendation</span><strong>{aiMetrics.cases_missing_ai_recommendation}</strong></div>
      </div>
    </CardFrame>
  );
}

function Distribution({ title, values, percentages }: { title: string; values: Record<string, number>; percentages: Record<string, number> }) {
  return (
    <div>
      <h4>{title}</h4>
      <div className="metric-bars compact">
        {entries(values).length === 0 ? <div className="empty-state">No values yet.</div> : entries(values).map(([key, count]) => (
          <div className="metric-bar-row" key={key}>
            <div className="metric-bar-label"><span>{key}</span><strong>{count} | {formatPercent(percentages[key] ?? 0)}</strong></div>
            <div className="metric-bar-track"><div className="metric-bar-fill" style={{ width: `${Math.min(percentages[key] ?? 0, 100)}%` }} /></div>
          </div>
        ))}
      </div>
    </div>
  );
}
