"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { IncidentList } from "@/components/incidents/IncidentList";
import { getIncidents } from "@/services/incidentService";
import type { Incident } from "@/types/incident.types";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { getIncidents().then((response) => setIncidents(response.incidents)).catch((err: Error) => setError(err.message)).finally(() => setLoading(false)); }, []);
  return (
    <ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-shell">
      <Header title="Incidents" subtitle="Operational incident lifecycle and response tracking." />
      <section className="content">{loading ? <LoadingSpinner label="Loading incidents" /> : error ? <ErrorMessage message={error} /> : <IncidentList incidents={incidents} />}</section>
    </main></div></ProtectedRoute>
  );
}
