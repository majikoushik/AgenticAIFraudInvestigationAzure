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
              <h4>{event.event_type} <span className="badge status-badge">{event.event_category}</span></h4>
              <p>{event.description}</p>
              {(event.previous_status || event.new_status) && <p>
                {event.previous_status && event.new_status
                  ? `${event.previous_status} -> ${event.new_status}`
                  : "Status context not available."}
              </p>}
              {event.decision && <p>Decision: {event.decision} · Reason: {event.reason_code ?? "n/a"}</p>}
              {event.human_override && <p>Human override: {event.ai_recommendation} {"->"} {event.human_decision}. {event.override_reason}</p>}
              {event.agent_name && <p>Agent: {event.agent_name}</p>}
              {event.rag_sources.length > 0 && <p>RAG sources: {event.rag_sources.join(", ")}</p>}
              {event.error_message && <p>Error: {event.error_code ?? "n/a"} · {event.error_message}</p>}
              <p>{event.actor} ({event.actor_role}) · {formatDateTime(event.timestamp)}</p>
              {Object.keys(event.metadata).length > 0 && (
                <details>
                  <summary>Metadata</summary>
                  <pre className="code-block">{JSON.stringify(event.metadata, null, 2)}</pre>
                </details>
              )}
            </div>
          ))}
        </div>
      )}
    </CardFrame>
  );
}
