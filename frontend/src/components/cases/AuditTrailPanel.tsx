import { CardFrame } from "@/components/cases/CardFrame";
import type { AuditTrail } from "@/types/audit.types";
import { formatDateTime } from "@/utils/maskingUtils";

type AuditTrailPanelProps = {
  auditTrail: AuditTrail | null;
};

export function AuditTrailPanel({ auditTrail }: AuditTrailPanelProps) {
  return (
    <CardFrame title="Audit Trail" subtitle="Local in-memory audit entries from backend service.">
      {!auditTrail || auditTrail.entries.length === 0 ? (
        <div className="empty-state">No audit entries recorded yet.</div>
      ) : (
        <div className="panel-list">
          {auditTrail.entries.map((entry, index) => (
            <div className="panel-item" key={`${entry.created_at}-${index}`}>
              <h4>{entry.action} · {entry.decision ?? "no decision"}</h4>
              <p>{entry.comment ?? "No comment provided."}</p>
              <p>Reviewed by {entry.reviewed_by ?? "unknown"} on {formatDateTime(entry.created_at)}</p>
            </div>
          ))}
        </div>
      )}
    </CardFrame>
  );
}
