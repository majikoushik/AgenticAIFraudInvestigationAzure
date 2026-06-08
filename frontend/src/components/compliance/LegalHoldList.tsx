import { LegalHoldBadge } from "@/components/compliance/LegalHoldBadge";
import type { LegalHold } from "@/types/legalHold.types";

export function LegalHoldList({ holds }: { holds: LegalHold[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>Hold</th><th>Case</th><th>Record</th><th>Category</th><th>Status</th><th>Reason</th></tr></thead>
        <tbody>{holds.map((hold) => <tr key={hold.legal_hold_id}><td>{hold.legal_hold_id}</td><td>{hold.case_id ?? "-"}</td><td>{hold.record_id ?? "-"}</td><td>{hold.data_category ?? "-"}</td><td><LegalHoldBadge value={hold.status} /></td><td>{hold.reason}</td></tr>)}</tbody>
      </table>
    </div>
  );
}
