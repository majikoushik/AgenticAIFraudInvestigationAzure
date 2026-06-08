"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { RetentionPolicyEditor } from "@/components/compliance/RetentionPolicyEditor";
import { RetentionPolicyTable } from "@/components/compliance/RetentionPolicyTable";
import { RetentionScanPanel } from "@/components/compliance/RetentionScanPanel";
import { RetentionScanResultTable } from "@/components/compliance/RetentionScanResultTable";
import { getRetentionPolicies } from "@/services/retentionService";
import type { RetentionPolicy, RetentionScanResult } from "@/types/retention.types";

export default function RetentionPage() {
  const [policies, setPolicies] = useState<RetentionPolicy[]>([]);
  const [scan, setScan] = useState<RetentionScanResult | null>(null);
  useEffect(() => { getRetentionPolicies().then(setPolicies).catch(() => setPolicies([])); }, []);
  return (
    <ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-shell">
      <Header title="Retention Policies" subtitle="Policy registry, dry-run scanning, archive and purge eligibility." />
      <section className="content grid">
        <RetentionScanPanel onScan={setScan} />
        <section className="card"><div className="card-header"><h3>Policies</h3><p>Retention day values require legal approval before production use.</p></div><div className="card-body"><RetentionPolicyTable policies={policies} /></div></section>
        {policies[0] && <section className="card"><div className="card-header"><h3>Edit First Policy</h3><p>Retention days are edited through policy APIs, not generic config.</p></div><div className="card-body"><RetentionPolicyEditor policy={policies[0]} onSaved={(saved) => setPolicies((items) => items.map((item) => item.data_category === saved.data_category ? saved : item))} /></div></section>}
        {scan && <section className="card"><div className="card-header"><h3>Latest Scan</h3><p>{scan.records_scanned} records scanned. Purge defaults to dry-run.</p></div><div className="card-body"><RetentionScanResultTable candidates={scan.candidates} /></div></section>}
      </section>
    </main></div></ProtectedRoute>
  );
}
