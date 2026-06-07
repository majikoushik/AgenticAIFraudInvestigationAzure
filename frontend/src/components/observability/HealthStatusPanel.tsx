import { CardFrame } from "@/components/cases/CardFrame";
import type { HealthDetails } from "@/types/observability.types";

export function HealthStatusPanel({ details }: { details: HealthDetails }) {
  return (
    <CardFrame title="Health Checks" subtitle="Safe backend health details for operations.">
      <div className="meta-list">
        {Object.entries(details.checks).map(([key, value]) => (
          <div className="meta-row" key={key}>
            <span className="meta-label">{key}</span>
            <span className="meta-value">{value}</span>
          </div>
        ))}
      </div>
    </CardFrame>
  );
}
