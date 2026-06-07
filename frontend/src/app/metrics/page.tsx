"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { MetricsSummaryCards } from "@/components/metrics/MetricsSummaryCards";
import { CaseStatusChart } from "@/components/metrics/CaseStatusChart";
import { AiVsHumanPanel } from "@/components/metrics/AiVsHumanPanel";
import { HumanOverridePanel } from "@/components/metrics/HumanOverridePanel";
import { OperationalMetricsPanel } from "@/components/metrics/OperationalMetricsPanel";
import { AgentMetricsPanel } from "@/components/metrics/AgentMetricsPanel";
import { RagMetricsPanel } from "@/components/metrics/RagMetricsPanel";
import { AuditMetricsPanel } from "@/components/metrics/AuditMetricsPanel";
import { getMetricsSummary } from "@/services/metricsService";
import type { MetricsSummary } from "@/types/metrics.types";

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMetricsSummary()
      .then(setMetrics)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Evaluation Metrics" subtitle="AI recommendation quality, human acceptance, operational timing, RAG, agent, and audit metrics." />
        <section className="content">
          {loading ? (
            <LoadingSpinner label="Loading evaluation metrics" />
          ) : error ? (
            <ErrorMessage message={error} />
          ) : metrics ? (
            <div className="grid metrics-grid">
              <MetricsSummaryCards metrics={metrics} />
              <CaseStatusChart metrics={metrics.case_status_metrics} />
              <AiVsHumanPanel
                aiMetrics={metrics.ai_recommendation_metrics}
                decisionMetrics={metrics.human_decision_metrics}
                overrideMetrics={metrics.human_override_metrics}
              />
              <HumanOverridePanel metrics={metrics.human_override_metrics} />
              <OperationalMetricsPanel
                investigation={metrics.investigation_time_metrics}
                review={metrics.human_review_time_metrics}
              />
              <AgentMetricsPanel metrics={metrics.agent_execution_metrics} />
              <RagMetricsPanel rag={metrics.rag_retrieval_metrics} policy={metrics.policy_citation_metrics} />
              <AuditMetricsPanel metrics={metrics.audit_metrics} />
            </div>
          ) : (
            <div className="empty-state">Metrics are not available.</div>
          )}
        </section>
      </main>
    </div>
  );
}
