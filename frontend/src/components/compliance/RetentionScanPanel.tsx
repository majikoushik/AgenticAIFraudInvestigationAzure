"use client";

import { useState } from "react";
import { runRetentionScan } from "@/services/retentionService";
import type { RetentionScanResult } from "@/types/retention.types";

export function RetentionScanPanel({ onScan }: { onScan: (scan: RetentionScanResult) => void }) {
  const [dryRun, setDryRun] = useState(true);
  const [loading, setLoading] = useState(false);

  async function runScan() {
    setLoading(true);
    try {
      onScan(await runRetentionScan({ dry_run: dryRun }));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <div className="card-header">
        <h3>Retention Scan</h3>
        <p>Retention defaults are placeholders and must be approved by legal/compliance before production use.</p>
      </div>
      <div className="card-body inline-form">
        <label><input type="checkbox" checked={dryRun} onChange={(event) => setDryRun(event.target.checked)} /> Dry run</label>
        <button type="button" onClick={runScan} disabled={loading}>{loading ? "Scanning" : "Run Scan"}</button>
      </div>
    </section>
  );
}
