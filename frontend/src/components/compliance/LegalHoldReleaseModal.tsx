"use client";

import { useState } from "react";
import { releaseLegalHold } from "@/services/legalHoldService";
import type { LegalHold } from "@/types/legalHold.types";

export function LegalHoldReleaseModal({ onReleased }: { onReleased: (hold: LegalHold) => void }) {
  const [holdId, setHoldId] = useState("");
  const [reason, setReason] = useState("");
  async function submit() {
    if (!holdId || !reason) return;
    onReleased(await releaseLegalHold(holdId, reason));
    setHoldId("");
    setReason("");
  }
  return <section className="card"><div className="card-header"><h3>Release Legal Hold</h3><p>Release actions are audited.</p></div><div className="card-body inline-form"><input placeholder="Legal hold ID" value={holdId} onChange={(event) => setHoldId(event.target.value)} /><input placeholder="Release reason" value={reason} onChange={(event) => setReason(event.target.value)} /><button type="button" onClick={submit}>Release</button></div></section>;
}
