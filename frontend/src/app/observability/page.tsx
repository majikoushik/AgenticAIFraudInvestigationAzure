"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/common/Header";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { HealthStatusPanel } from "@/components/observability/HealthStatusPanel";
import { ObservabilitySummaryCards } from "@/components/observability/ObservabilitySummaryCards";
import { RecentTelemetryEventsPanel } from "@/components/observability/RecentTelemetryEventsPanel";
import { TelemetryConfigPanel } from "@/components/observability/TelemetryConfigPanel";
import { getHealthDetails, getRecentTelemetryEvents } from "@/services/observabilityService";
import type { HealthDetails, TelemetryEvent } from "@/types/observability.types";

export default function ObservabilityPage() {
  const [details, setDetails] = useState<HealthDetails | null>(null);
  const [events, setEvents] = useState<TelemetryEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getHealthDetails(), getRecentTelemetryEvents().catch(() => [])])
      .then(([health, telemetry]) => {
        setDetails(health);
        setEvents(telemetry);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Observability" subtitle="Health, telemetry configuration, and local sanitized telemetry events." />
        <section className="content">
          {loading ? (
            <LoadingSpinner label="Loading observability" />
          ) : error ? (
            <ErrorMessage message={error} />
          ) : details ? (
            <div className="grid detail-grid">
              <ObservabilitySummaryCards details={details} />
              <HealthStatusPanel details={details} />
              <TelemetryConfigPanel details={details} />
              <RecentTelemetryEventsPanel events={events} />
            </div>
          ) : (
            <div className="empty-state">Observability details are unavailable.</div>
          )}
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
