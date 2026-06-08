"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { ComplianceSummaryCards } from "@/components/compliance/ComplianceSummaryCards";
import { getComplianceSummary } from "@/services/complianceService";
import type { ComplianceSummary } from "@/types/compliance.types";

export default function CompliancePage() {
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  useEffect(() => { getComplianceSummary().then(setSummary).catch(() => setSummary(null)); }, []);
  return (
    <ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-shell">
      <Header title="Compliance" subtitle="Data retention, legal hold, export, and review posture." />
      <section className="content">
        <ComplianceSummaryCards summary={summary} />
        <section className="card"><div className="card-header"><h3>Warnings</h3><p>Retention defaults are placeholders and must be approved by legal/compliance before production use.</p></div><div className="card-body"><pre className="code-block">{JSON.stringify(summary?.compliance_warnings ?? [], null, 2)}</pre></div></section>
      </section>
    </main></div></ProtectedRoute>
  );
}
