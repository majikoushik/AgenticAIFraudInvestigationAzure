"use client";

import { useState } from "react";
import { simulateAlert } from "@/services/alertService";

export function AlertSimulationPanel({ onSimulated }: { onSimulated: () => void }) {
  const [busy, setBusy] = useState(false);
  async function simulate() {
    setBusy(true);
    await simulateAlert({
      alert_type: "HIGH_AGENT_FAILURE_RATE",
      severity: "SEV1_HIGH",
      title: "Simulated high agent failure",
      description: "Testing local alert-to-incident response flow."
    });
    setBusy(false);
    onSimulated();
  }
  return <button className="button" onClick={simulate} disabled={busy}>{busy ? "Simulating" : "Simulate SEV1 Alert"}</button>;
}
