"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/common/Header";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { CostSummaryCards } from "@/components/cost/CostSummaryCards";
import { PricingConfigWarning } from "@/components/cost/PricingConfigWarning";
import { TokenUsagePanel } from "@/components/cost/TokenUsagePanel";
import { DailyCostTrendPanel } from "@/components/cost/DailyCostTrendPanel";
import { AgentCostTable } from "@/components/cost/AgentCostTable";
import { ModelCostTable } from "@/components/cost/ModelCostTable";
import { TopExpensiveCasesTable } from "@/components/cost/TopExpensiveCasesTable";
import { BudgetStatusPanel } from "@/components/cost/BudgetStatusPanel";
import { CostAnomalyPanel } from "@/components/cost/CostAnomalyPanel";
import { getCostDashboard } from "@/services/costService";

type Dashboard = Awaited<ReturnType<typeof getCostDashboard>>;

export default function CostPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCostDashboard()
      .then(setDashboard)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <ProtectedRoute>
      <div className="app-layout">
        <Sidebar />
        <main className="main-shell">
          <Header title="Cost Monitoring" subtitle="Estimated token usage, model cost, agent cost, budget status, and anomaly indicators." />
          <section className="content">
            {loading ? (
              <LoadingSpinner label="Loading cost dashboard" />
            ) : error ? (
              <ErrorMessage message={error} />
            ) : dashboard ? (
              <div className="grid metrics-grid">
                <PricingConfigWarning configured={dashboard.summary.pricing_configured} />
                <CostSummaryCards summary={dashboard.summary} />
                <TokenUsagePanel usage={dashboard.tokenUsage} />
                <BudgetStatusPanel budget={dashboard.budget} currency={dashboard.summary.currency} />
                <DailyCostTrendPanel trend={dashboard.trend} currency={dashboard.summary.currency} />
                <AgentCostTable agents={dashboard.agents} currency={dashboard.summary.currency} />
                <ModelCostTable models={dashboard.models} currency={dashboard.summary.currency} />
                <TopExpensiveCasesTable cases={dashboard.topCases} currency={dashboard.summary.currency} />
                <CostAnomalyPanel anomalies={dashboard.anomalies} />
              </div>
            ) : (
              <div className="empty-state">Cost monitoring data is not available.</div>
            )}
          </section>
        </main>
      </div>
    </ProtectedRoute>
  );
}
