"use client";

import Link from "next/link";
import { useAuth } from "@/auth/useAuth";
import { AcceptCaseButton } from "@/components/assignment/AcceptCaseButton";
import { AssignmentPriorityBadge } from "@/components/assignment/AssignmentPriorityBadge";
import { AssignmentStatusBadge } from "@/components/assignment/AssignmentStatusBadge";
import { SlaStatusBadge } from "@/components/assignment/SlaStatusBadge";
import { releaseCase } from "@/services/assignmentService";
import type { QueueCase } from "@/types/assignment.types";
import { formatDateTime, normalizeRiskClass } from "@/utils/maskingUtils";

type Props = {
  cases: QueueCase[];
  title: string;
  onRefresh: () => void;
};

export function CaseQueueTable({ cases, title, onRefresh }: Props) {
  const { user, hasPermission } = useAuth();

  async function handleRelease(caseId: string) {
    if (!user) return;
    await releaseCase(caseId, user.user_id, "Queue release", "Released from queue view.");
    onRefresh();
  }

  return (
    <section className="card">
      <div className="card-header">
        <h3>{title}</h3>
        <p>{cases.length} cases match the current queue view.</p>
      </div>
      <div className="table-wrap">
        {cases.length === 0 ? (
          <div className="empty-state">No cases in this queue.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Alert Type</th>
                <th>Risk</th>
                <th>Case Status</th>
                <th>Assignment</th>
                <th>Assigned To</th>
                <th>Priority</th>
                <th>SLA</th>
                <th>SLA Due</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((item) => (
                <tr key={item.case_id}>
                  <td>{item.case_id}</td>
                  <td>{item.alert_type}</td>
                  <td><span className={`badge ${normalizeRiskClass(item.risk_level)}`}>{item.risk_level}</span></td>
                  <td><span className="badge status-badge">{item.case_status}</span></td>
                  <td><AssignmentStatusBadge status={item.assignment_status} /></td>
                  <td>{item.assigned_to_name ?? item.assigned_to ?? "Unassigned"}</td>
                  <td><AssignmentPriorityBadge priority={item.assignment_priority} /></td>
                  <td><SlaStatusBadge status={item.sla_status} /></td>
                  <td>{item.sla_due_at ? formatDateTime(item.sla_due_at) : "Not set"}</td>
                  <td>{formatDateTime(item.created_at)}</td>
                  <td>
                    <div className="action-row">
                      <Link className="button secondary" href={`/cases/${item.case_id}`}>View</Link>
                      {hasPermission("ACCEPT_CASE") && user && (
                        <AcceptCaseButton caseId={item.case_id} userId={user.user_id} disabled={Boolean(item.assigned_to && item.assigned_to !== user.user_id && user.role !== "FRAUD_MANAGER" && user.role !== "ADMIN")} onDone={onRefresh} />
                      )}
                      {hasPermission("RELEASE_CASE") && item.assigned_to === user?.user_id && (
                        <button className="button secondary" onClick={() => handleRelease(item.case_id)}>Release</button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
