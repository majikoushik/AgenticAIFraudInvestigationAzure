"use client";

import { useState } from "react";
import { createCaseComplianceExport } from "@/services/complianceService";
import type { ComplianceExport } from "@/types/compliance.types";

export function ComplianceExportPanel({ onCreated }: { onCreated: (item: ComplianceExport) => void }) {
  const [caseId, setCaseId] = useState("");
  async function submit() {
    if (!caseId) return;
    onCreated(await createCaseComplianceExport(caseId, { include_audit: true, include_ai_outputs: true, include_feedback: true, redact_pii: true }));
    setCaseId("");
  }
  return <section className="card"><div className="card-header"><h3>Create Case Export</h3><p>PII redaction is enabled by default. Raw prompts and raw model responses are excluded.</p></div><div className="card-body inline-form"><input placeholder="Case ID" value={caseId} onChange={(event) => setCaseId(event.target.value)} /><button type="button" onClick={submit}>Create Export</button></div></section>;
}
