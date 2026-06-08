import { DataClassificationBadge } from "@/components/compliance/DataClassificationBadge";
import { LegalHoldBadge } from "@/components/compliance/LegalHoldBadge";
import { RetentionStatusBadge } from "@/components/compliance/RetentionStatusBadge";
import type { RetentionCandidate } from "@/types/retention.types";

export function RetentionScanResultTable({ candidates }: { candidates: RetentionCandidate[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>Record</th><th>Category</th><th>Class</th><th>Status</th><th>Action</th><th>Hold</th><th>Reason</th></tr></thead>
        <tbody>
          {candidates.map((candidate) => (
            <tr key={`${candidate.data_category}-${candidate.record_id}`}>
              <td>{candidate.record_id}</td>
              <td>{candidate.data_category}</td>
              <td><DataClassificationBadge value={candidate.classification} /></td>
              <td><RetentionStatusBadge value={candidate.retention_status} /></td>
              <td>{candidate.recommended_action}</td>
              <td><LegalHoldBadge value={candidate.legal_hold_status} /></td>
              <td>{candidate.reason}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
