import type { AdminConfigHistoryRecord } from "@/types/adminConfig.types";

export function ConfigHistoryPanel({ history }: { history: AdminConfigHistoryRecord[] }) {
  return (
    <section className="panel span-2">
      <h2>Config History</h2>
      {history.length === 0 ? <div className="empty-state">No configuration changes recorded.</div> : (
        <div className="table-wrap"><table><thead><tr><th>Key</th><th>Old</th><th>New</th><th>Updated by</th><th>Timestamp</th><th>Comment</th></tr></thead>
          <tbody>{history.map((item) => <tr key={item.history_id}><td>{item.key}</td><td>{String(item.old_value)}</td><td>{String(item.new_value)}</td><td>{item.updated_by}</td><td>{item.updated_at}</td><td>{item.comment ?? "-"}</td></tr>)}</tbody>
        </table></div>
      )}
    </section>
  );
}
