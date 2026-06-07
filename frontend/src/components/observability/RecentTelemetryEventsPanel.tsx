import { CardFrame } from "@/components/cases/CardFrame";
import type { TelemetryEvent } from "@/types/observability.types";

export function RecentTelemetryEventsPanel({ events }: { events: TelemetryEvent[] }) {
  return (
    <CardFrame title="Recent Telemetry Events" subtitle="Local sanitized telemetry events when Application Insights is not configured." fullSpan>
      {events.length === 0 ? (
        <div className="empty-state">No local telemetry events found.</div>
      ) : (
        <div className="panel-list">
          {events.slice(-20).reverse().map((event, index) => (
            <div className="panel-item" key={`${event.timestamp}-${index}`}>
              <h4>{event.name}</h4>
              <p>{event.timestamp} - {event.telemetry_type}</p>
              <pre className="code-block">{JSON.stringify({ properties: event.properties, measurements: event.measurements }, null, 2)}</pre>
            </div>
          ))}
        </div>
      )}
    </CardFrame>
  );
}
