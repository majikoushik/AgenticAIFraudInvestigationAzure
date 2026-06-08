"use client";

import { useState } from "react";
import { createLegalHold } from "@/services/legalHoldService";
import type { LegalHold } from "@/types/legalHold.types";

export function LegalHoldCreateModal({ onCreated }: { onCreated: (hold: LegalHold) => void }) {
  const [caseId, setCaseId] = useState("");
  const [reason, setReason] = useState("");
  async function submit() {
    if (!reason) return;
    onCreated(await createLegalHold({ case_id: caseId || undefined, reason }));
    setCaseId("");
    setReason("");
  }
  return <section className="card"><div className="card-header"><h3>Create Legal Hold</h3><p>Active legal holds block purge.</p></div><div className="card-body inline-form"><input placeholder="Case ID" value={caseId} onChange={(event) => setCaseId(event.target.value)} /><input placeholder="Reason" value={reason} onChange={(event) => setReason(event.target.value)} /><button type="button" onClick={submit}>Create</button></div></section>;
}
