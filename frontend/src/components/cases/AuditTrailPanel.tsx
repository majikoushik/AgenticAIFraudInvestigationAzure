import { CardFrame } from "@/components/cases/CardFrame";
import type { AuditTrail } from "@/types/audit.types";
import { formatDateTime } from "@/utils/maskingUtils";

type AuditTrailPanelProps = {
  auditTrail: AuditTrail | null;
};

export function AuditTrailPanel({ auditTrail }: AuditTrailPanelProps) {
  return (
    <CardFrame title="Audit Trail" subtitle="Chronological human review and status lifecycle events.">
      {!auditTrail || auditTrail.events.length === 0 ? (
        <div className="empty-state">No audit events recorded yet.</div>
      ) : (
        <div className="timeline">
          {auditTrail.events.map((event) => (
            <div className="timeline-item" key={event.audit_id}>
              <h4>{event.event_type}</h4>
              <p>
                {event.previous_status && event.new_status
                  ? `${event.previous_status} -> ${event.new_status}`
                  : event.comment ?? "Workflow event recorded."}
              </p>
              {event.decision && <p>Decision: {event.decision} · Reason: {event.reason_code ?? "n/a"}</p>}
              {event.human_override && <p>Human override: {event.ai_recommendation} {"->"} {event.human_decision}. {event.override_reason}</p>}
              <p>{event.actor} ({event.actor_role}) · {formatDateTime(event.timestamp)}</p>
            </div>
          ))}
        </div>
      )}
    </CardFrame>
  );
}
