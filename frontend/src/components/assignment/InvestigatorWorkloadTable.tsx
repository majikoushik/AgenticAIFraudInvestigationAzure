import type { InvestigatorWorkload } from "@/types/assignment.types";

export function InvestigatorWorkloadTable({ investigators }: { investigators: InvestigatorWorkload[] }) {
  return (
    <section className="card">
      <div className="card-header">
        <h3>Investigator Workload</h3>
        <p>Local demo workload derived from assigned synthetic cases.</p>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Investigator</th>
              <th>Role</th>
              <th>Team</th>
              <th>Active</th>
              <th>Accepted</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {investigators.map((item) => (
              <tr key={item.user_id}>
                <td>{item.display_name}</td>
                <td>{item.role}</td>
                <td>{item.team}</td>
                <td>{item.active_case_count}</td>
                <td>{item.accepted_case_count}</td>
                <td><span className="badge status-badge">{item.workload_status}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
