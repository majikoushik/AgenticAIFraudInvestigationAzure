import { CardFrame } from "@/components/cases/CardFrame";
import type { HealthDetails } from "@/types/observability.types";

export function TelemetryConfigPanel({ details }: { details: HealthDetails }) {
  return (
    <CardFrame title="Telemetry Config" subtitle="Secret-free observability configuration summary.">
      <div className="meta-list">
        {Object.entries(details.observability).map(([key, value]) => (
          <div className="meta-row" key={key}>
            <span className="meta-label">{key}</span>
            <span className="meta-value">{String(value)}</span>
          </div>
        ))}
      </div>
    </CardFrame>
  );
}
