import { CardFrame } from "@/components/cases/CardFrame";
import type { OverrideSummary } from "@/types/review.types";
import { formatDateTime } from "@/utils/maskingUtils";

type HumanOverrideBannerProps = {
  overrideSummary: OverrideSummary | null;
};

export function HumanOverrideBanner({ overrideSummary }: HumanOverrideBannerProps) {
  if (!overrideSummary?.has_override) {
    return null;
  }

  return (
    <CardFrame title="Human Override Detected" subtitle="The reviewer selected a final decision that differs from the AI recommendation.">
      <div className="message warning">
        Human override detected
      </div>
      <div className="facts-grid">
        <div>
          <span className="label">AI recommendation</span>
          <strong>{overrideSummary.ai_recommendation ?? "Not available"}</strong>
        </div>
        <div>
          <span className="label">Human decision</span>
          <strong>{overrideSummary.human_decision ?? "Not available"}</strong>
        </div>
        <div>
          <span className="label">Detected by</span>
          <strong>{overrideSummary.override_detected_by ?? "Not available"}</strong>
        </div>
        <div>
          <span className="label">Detected at</span>
          <strong>{overrideSummary.override_detected_at ? formatDateTime(overrideSummary.override_detected_at) : "Not available"}</strong>
        </div>
      </div>
      <p>{overrideSummary.override_reason}</p>
    </CardFrame>
  );
}
