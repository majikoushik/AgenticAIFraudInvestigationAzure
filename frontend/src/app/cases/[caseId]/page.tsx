"use client";

import { useCallback, useEffect, useState } from "react";
import { Header } from "@/components/common/Header";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Sidebar } from "@/components/common/Sidebar";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";
import { ErrorMessage } from "@/components/common/ErrorMessage";
import { CaseSummaryCard } from "@/components/cases/CaseSummaryCard";
import { CustomerProfileCard } from "@/components/cases/CustomerProfileCard";
import { TransactionDetailsCard } from "@/components/cases/TransactionDetailsCard";
import { BeneficiaryDetailsCard } from "@/components/cases/BeneficiaryDetailsCard";
import { DeviceLocationCard } from "@/components/cases/DeviceLocationCard";
import { RiskIndicatorPanel } from "@/components/cases/RiskIndicatorPanel";
import { AgentTracePanel } from "@/components/cases/AgentTracePanel";
import { PolicyReferencePanel } from "@/components/cases/PolicyReferencePanel";
import { SimilarCasesPanel } from "@/components/cases/SimilarCasesPanel";
import { ReviewerValidationPanel } from "@/components/cases/ReviewerValidationPanel";
import { HumanDecisionPanel } from "@/components/cases/HumanDecisionPanel";
import { AuditTrailPanel } from "@/components/cases/AuditTrailPanel";
import { HumanOverrideBanner } from "@/components/cases/HumanOverrideBanner";
import { StatusLifecyclePanel } from "@/components/cases/StatusLifecyclePanel";
import { getAuditTrail } from "@/services/auditService";
import { runInvestigation } from "@/services/agentService";
import { getCaseDetail } from "@/services/caseService";
import { getCaseStatus } from "@/services/statusService";
import type { InvestigationPackage } from "@/types/agent.types";
import type { AuditTrail } from "@/types/audit.types";
import type { CaseDetail } from "@/types/case.types";
import type { CaseStatusInfo } from "@/types/status.types";

type PageProps = {
  params: Promise<{ caseId: string }>;
};

export default function CaseDetailPage({ params }: PageProps) {
  const [caseId, setCaseId] = useState<string>("");
  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null);
  const [auditTrail, setAuditTrail] = useState<AuditTrail | null>(null);
  const [statusInfo, setStatusInfo] = useState<CaseStatusInfo | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationPackage | null>(null);
  const [loading, setLoading] = useState(true);
  const [investigating, setInvestigating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    params.then((resolved) => setCaseId(resolved.caseId));
  }, [params]);

  const refreshCase = useCallback(async () => {
    if (!caseId) {
      return;
    }
    const [detail, audit, status] = await Promise.all([getCaseDetail(caseId), getAuditTrail(caseId), getCaseStatus(caseId)]);
    setCaseDetail(detail);
    setAuditTrail(audit);
    setStatusInfo(status);
  }, [caseId]);

  useEffect(() => {
    if (!caseId) {
      return;
    }

    Promise.all([getCaseDetail(caseId), getAuditTrail(caseId), getCaseStatus(caseId)])
      .then(([detail, audit, status]) => {
        setCaseDetail(detail);
        setAuditTrail(audit);
        setStatusInfo(status);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [caseId]);

  async function handleRunInvestigation() {
    setInvestigating(true);
    setError(null);
    try {
      setInvestigation(await runInvestigation(caseId));
      await refreshCase();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setInvestigating(false);
    }
  }

  async function handleDecisionRecorded() {
    setAuditTrail(await getAuditTrail(caseId));
    await refreshCase();
  }

  return (
    <ProtectedRoute><div className="app-layout">
      <Sidebar />
      <main className="main-shell">
        <Header title="Case Investigation" subtitle={caseId ? `Detailed review workspace for ${caseId}` : "Loading case"} />
        <section className="content">
          {loading ? (
            <LoadingSpinner label="Loading case detail" />
          ) : error ? (
            <ErrorMessage message={error} />
          ) : caseDetail ? (
            <div className="grid detail-grid">
              <div className="page-heading full-span">
                <div>
                  <h2>{caseDetail.metadata.case_id}</h2>
                  <p>{caseDetail.metadata.reason}</p>
                </div>
                <button className="button" onClick={handleRunInvestigation} disabled={investigating}>
                  {investigating ? "Running Investigation" : "Run AI Investigation"}
                </button>
              </div>

              {caseDetail.override_summary?.has_override && (
                <div className="full-span">
                  <HumanOverrideBanner overrideSummary={caseDetail.override_summary} />
                </div>
              )}
              <CaseSummaryCard caseDetail={caseDetail} />
              <StatusLifecyclePanel statusInfo={statusInfo} />
              <CustomerProfileCard customer={caseDetail.customer} />
              <TransactionDetailsCard transaction={caseDetail.suspicious_transaction} />
              <BeneficiaryDetailsCard beneficiary={caseDetail.beneficiary} />
              <DeviceLocationCard device={caseDetail.device} />
              <RiskIndicatorPanel indicators={caseDetail.initial_risk_indicators} title="Initial Risk Indicators" />

              {investigating && (
                <div className="full-span card">
                  <div className="card-body">
                    <LoadingSpinner label="Running local agent orchestration" />
                  </div>
                </div>
              )}

              {investigation && (
                <>
                  <RiskIndicatorPanel indicators={investigation.risk_indicators} title="AI Investigation Result" summary={investigation.investigation_summary} />
                  <AgentTracePanel trace={investigation.agent_trace} />
                  <PolicyReferencePanel references={investigation.policy_references} />
                  <SimilarCasesPanel cases={investigation.similar_cases} />
                  <ReviewerValidationPanel validation={investigation.reviewer_validation} humanReviewRequired={investigation.human_review_required} />
                </>
              )}

              <HumanDecisionPanel
                caseId={caseId}
                currentStatus={caseDetail.current_status}
                aiRecommendation={caseDetail.ai_recommendation}
                onDecisionRecorded={handleDecisionRecorded}
              />
              <AuditTrailPanel auditTrail={auditTrail} />
            </div>
          ) : (
            <div className="empty-state">Case detail is not available.</div>
          )}
        </section>
      </main>
    </div></ProtectedRoute>
  );
}
