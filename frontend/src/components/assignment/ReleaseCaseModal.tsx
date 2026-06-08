"use client";

import { useState } from "react";
import { releaseCase } from "@/services/assignmentService";

export function ReleaseCaseModal({ caseId, userId, onDone }: { caseId: string; userId: string; onDone: () => void }) {
  const [reason, setReason] = useState("Shift ended");

  async function handleSubmit() {
    await releaseCase(caseId, userId, reason, "Released from case detail.");
    onDone();
  }

  return (
    <div className="panel-item">
      <h4>Release Case</h4>
      <div className="form-grid">
        <input aria-label="Release reason" value={reason} onChange={(event) => setReason(event.target.value)} />
        <button className="button secondary" onClick={handleSubmit}>Release</button>
      </div>
    </div>
  );
}
