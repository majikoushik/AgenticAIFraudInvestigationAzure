import { CardFrame } from "@/components/cases/CardFrame";
import { formatDuration } from "@/components/metrics/metricsFormat";
import type { HumanReviewTimeMetrics, InvestigationTimeMetrics } from "@/types/metrics.types";

type OperationalMetricsPanelProps = {
  investigation: InvestigationTimeMetrics;
  review: HumanReviewTimeMetrics;
};

export function OperationalMetricsPanel({ investigation, review }: OperationalMetricsPanelProps) {
  return (
    <CardFrame title="Operational Timings" subtitle="Elapsed time from audit event pairs.">
      <div className="facts-grid">
        <div><span className="label">Avg AI investigation</span><strong>{formatDuration(investigation.average_ai_investigation_duration_seconds)}</strong></div>
        <div><span className="label">Min / Max AI investigation</span><strong>{formatDuration(investigation.minimum_ai_investigation_duration_seconds)} / {formatDuration(investigation.maximum_ai_investigation_duration_seconds)}</strong></div>
        <div><span className="label">Avg review wait</span><strong>{formatDuration(review.average_human_review_wait_time_seconds)}</strong></div>
        <div><span className="label">Min / Max review wait</span><strong>{formatDuration(review.minimum_human_review_wait_time_seconds)} / {formatDuration(review.maximum_human_review_wait_time_seconds)}</strong></div>
        <div><span className="label">Missing investigation durations</span><strong>{investigation.cases_with_missing_investigation_duration}</strong></div>
        <div><span className="label">Missing review durations</span><strong>{review.cases_with_missing_review_duration}</strong></div>
      </div>
    </CardFrame>
  );
}
