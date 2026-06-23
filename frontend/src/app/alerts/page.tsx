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
  useEffect(() => {
    let mounted = true;
    const doLoad = async () => {
      try {
        const response = await getAlerts();
        if (mounted) setAlerts(response.alerts);
      } catch (err: unknown) {
        if (mounted) setError(err instanceof Error ? err.message : String(err));
      } finally {
        if (mounted) setLoading(false);
      }
    };
    doLoad();
    return () => { mounted = false; };
  }, []);
  async function evaluate() {
    await evaluateAlerts();
    setLoading(true);
    try {
      const response = await getAlerts();
      setAlerts(response.alerts);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }
  return (
    <ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-shell">
      <Header title="Alerts" subtitle="Operational alert rules, local simulation, and active alert signals." />
      <section className="content">
        <div className="page-heading"><div><h2>Alert Center</h2><p>Simulate and evaluate alerts locally without Azure Monitor.</p></div><div className="stack"><button className="button secondary" onClick={evaluate}>Evaluate Rules</button><AlertSimulationPanel onSimulated={async () => { setLoading(true); try { const response = await getAlerts(); setAlerts(response.alerts); } catch (err: unknown) { setError(err instanceof Error ? err.message : String(err)); } finally { setLoading(false); } }} /></div></div>
        {loading ? <LoadingSpinner label="Loading alerts" /> : error ? <ErrorMessage message={error} /> : <AlertList alerts={alerts} />}
      </section>
    </main></div></ProtectedRoute>
  );
}
