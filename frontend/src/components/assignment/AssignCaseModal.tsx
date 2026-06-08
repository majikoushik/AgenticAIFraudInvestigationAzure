"use client";

import { useState } from "react";
import { assignCase } from "@/services/assignmentService";
import type { AssignmentPriority } from "@/types/assignment.types";

type Props = {
  caseId: string;
  onDone: () => void;
};

export function AssignCaseModal({ caseId, onDone }: Props) {
  const [assignedTo, setAssignedTo] = useState("fraud_analyst_01");
  const [displayName, setDisplayName] = useState("Fraud Analyst 01");
  const [priority, setPriority] = useState<AssignmentPriority>("HIGH");
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit() {
    await assignCase(caseId, {
      assigned_to: assignedTo,
      assigned_to_name: displayName,
      assigned_to_role: "FRAUD_ANALYST",
      assigned_team: "Fraud Operations",
      assignment_priority: priority,
      comment: "Assigned from investigator queue UI."
    });
    setMessage("Case assigned.");
    onDone();
  }

  return (
    <div className="panel-item">
      <h4>Assign Case</h4>
      <div className="form-grid">
        <input aria-label="Assigned user ID" value={assignedTo} onChange={(event) => setAssignedTo(event.target.value)} />
        <input aria-label="Assigned display name" value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
        <select aria-label="Priority" value={priority} onChange={(event) => setPriority(event.target.value as AssignmentPriority)}>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
        <button className="button" onClick={handleSubmit}>Assign</button>
        {message && <p className="caption">{message}</p>}
      </div>
    </div>
  );
}
