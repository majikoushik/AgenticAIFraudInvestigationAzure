import type { IncidentTimelineEvent } from "@/types/incident.types";

export function IncidentTimeline({ timeline }: { timeline: IncidentTimelineEvent[] }) {
  return (
    <div className="panel-list">
      {timeline.map((event, index) => <div className="panel-item" key={`${event.timestamp}-${index}`}><h4>{event.action}</h4><p>{event.timestamp} by {event.actor}</p><p>{event.comment}</p></div>)}
    </div>
  );
}
