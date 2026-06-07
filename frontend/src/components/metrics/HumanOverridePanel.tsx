import { CardFrame } from "@/components/cases/CardFrame";
import { formatPercent } from "@/components/metrics/metricsFormat";
import type { HumanOverrideMetrics } from "@/types/metrics.types";

type HumanOverridePanelProps = {
  metrics: HumanOverrideMetrics;
};

export function HumanOverridePanel({ metrics }: HumanOverridePanelProps) {
  return (
    <CardFrame title="Human Overrides" subtitle="Where reviewer decisions diverge from AI recommendations.">
      <div className="facts-grid">
        <div><span className="label">Reviewed cases</span><strong>{metrics.total_reviewed_cases}</strong></div>
        <div><span className="label">Overrides</span><strong>{metrics.total_overrides}</strong></div>
        <div><span className="label">Override rate</span><strong>{formatPercent(metrics.override_rate_percentage)}</strong></div>
      </div>
      {metrics.override_pairs.length === 0 ? (
        <div className="empty-state">No override pairs recorded yet.</div>
      ) : (
        <table className="table">
          <thead>
            <tr><th>AI Recommendation</th><th>Human Decision</th><th>Count</th></tr>
          </thead>
          <tbody>
            {metrics.override_pairs.map((pair) => (
              <tr key={`${pair.ai_recommendation}-${pair.human_decision}`}>
                <td>{pair.ai_recommendation}</td>
                <td>{pair.human_decision}</td>
                <td>{pair.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </CardFrame>
  );
}
