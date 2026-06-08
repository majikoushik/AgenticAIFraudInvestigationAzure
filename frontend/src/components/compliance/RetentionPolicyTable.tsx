import { DataClassificationBadge } from "@/components/compliance/DataClassificationBadge";
import type { RetentionPolicy } from "@/types/retention.types";

export function RetentionPolicyTable({ policies }: { policies: RetentionPolicy[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>Category</th><th>Class</th><th>Retain</th><th>Archive</th><th>Purge</th><th>Approval</th><th>Enabled</th></tr></thead>
        <tbody>
          {policies.map((policy) => (
            <tr key={policy.data_category}>
              <td>{policy.data_category}</td>
              <td><DataClassificationBadge value={policy.classification} /></td>
              <td>{policy.retention_days}d</td>
              <td>{policy.archive_after_days}d</td>
              <td>{policy.purge_after_days}d</td>
              <td>{policy.requires_approval_for_purge ? "Required" : "Not required"}</td>
              <td>{policy.enabled ? "Yes" : "No"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
