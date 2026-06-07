"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { AlertList } from "@/components/alerts/AlertList";
import { AlertSimulationPanel } from "@/components/alerts/AlertSimulationPanel";
import { evaluateAlerts, getAlerts } from "@/services/alertService";
import type { AlertEvent } from "@/types/alert.types";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  async function load() { const response = await getAlerts(); setAlerts(response.alerts); }
  useEffect(() => { load().catch((err: Error) => setError(err.message)).finally(() => setLoading(false)); }, []);
  async function evaluate() { await evaluateAlerts(); await load(); }
  return (
    <ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-shell">
      <Header title="Alerts" subtitle="Operational alert rules, local simulation, and active alert signals." />
      <section className="content">
        <div className="page-heading"><div><h2>Alert Center</h2><p>Simulate and evaluate alerts locally without Azure Monitor.</p></div><div className="stack"><button className="button secondary" onClick={evaluate}>Evaluate Rules</button><AlertSimulationPanel onSimulated={load} /></div></div>
        {loading ? <LoadingSpinner label="Loading alerts" /> : error ? <ErrorMessage message={error} /> : <AlertList alerts={alerts} />}
      </section>
    </main></div></ProtectedRoute>
  );
}
