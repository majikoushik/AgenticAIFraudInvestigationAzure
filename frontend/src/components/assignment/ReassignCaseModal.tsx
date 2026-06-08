"use client";

import { useState } from "react";
import { reassignCase } from "@/services/assignmentService";

export function ReassignCaseModal({ caseId, onDone }: { caseId: string; onDone: () => void }) {
  const [assignedTo, setAssignedTo] = useState("fraud_analyst_02");
  const [displayName, setDisplayName] = useState("Fraud Analyst 02");

  async function handleSubmit() {
    await reassignCase(caseId, {
      assigned_to: assignedTo,
      assigned_to_name: displayName,
      assigned_to_role: "FRAUD_ANALYST",
      assigned_team: "Fraud Operations",
      assignment_priority: "MEDIUM",
      comment: "Reassigned from investigator queue UI."
    });
    onDone();
  }

  return (
    <div className="panel-item">
      <h4>Reassign Case</h4>
      <div className="form-grid">
        <input aria-label="Reassigned user ID" value={assignedTo} onChange={(event) => setAssignedTo(event.target.value)} />
        <input aria-label="Reassigned display name" value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
        <button className="button secondary" onClick={handleSubmit}>Reassign</button>
      </div>
    </div>
  );
}
