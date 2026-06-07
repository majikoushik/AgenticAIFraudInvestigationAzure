"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { IncidentActionPanel } from "@/components/incidents/IncidentActionPanel";
import { IncidentDetail } from "@/components/incidents/IncidentDetail";
import { getIncident } from "@/services/incidentService";
import type { Incident } from "@/types/incident.types";

type PageProps = { params: Promise<{ incidentId: string }> };

export default function IncidentDetailPage({ params }: PageProps) {
  const [incidentId, setIncidentId] = useState("");
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { params.then((resolved) => setIncidentId(resolved.incidentId)); }, [params]);
  useEffect(() => {
    if (!incidentId) return;
    getIncident(incidentId).then(setIncident).catch((err: Error) => setError(err.message)).finally(() => setLoading(false));
  }, [incidentId]);
  return (
    <ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-shell">
      <Header title="Incident Detail" subtitle={incidentId || "Loading incident"} />
      <section className="content">
        {loading ? <LoadingSpinner label="Loading incident" /> : error ? <ErrorMessage message={error} /> : incident ? (
          <div className="grid detail-grid"><IncidentDetail incident={incident} /><IncidentActionPanel incident={incident} onUpdated={setIncident} /></div>
        ) : <div className="empty-state">Incident not found.</div>}
      </section>
    </main></div></ProtectedRoute>
  );
}
