"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { ComplianceExportList } from "@/components/compliance/ComplianceExportList";
import { ComplianceExportPanel } from "@/components/compliance/ComplianceExportPanel";
import { getComplianceExports } from "@/services/complianceService";
import type { ComplianceExport } from "@/types/compliance.types";

export default function ComplianceExportsPage() {
  const [exports, setExports] = useState<ComplianceExport[]>([]);
  useEffect(() => { getComplianceExports().then(setExports).catch(() => setExports([])); }, []);
  return <ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-shell"><Header title="Compliance Exports" subtitle="Sanitized case packages for audit, legal, or regulatory review." /><section className="content grid"><ComplianceExportPanel onCreated={(item) => setExports((items) => [item, ...items])} /><section className="card"><div className="card-header"><h3>Exports</h3><p>Raw prompts, raw model responses, chain-of-thought, and secrets are excluded.</p></div><div className="card-body"><ComplianceExportList exports={exports} /></div></section></section></main></div></ProtectedRoute>;
}
