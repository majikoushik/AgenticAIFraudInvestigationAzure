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
import { AiProviderBadge } from "@/components/cases/AiProviderBadge";
import { PolicyReferencePanel } from "@/components/cases/PolicyReferencePanel";
import { SimilarCasesPanel } from "@/components/cases/SimilarCasesPanel";
import { ReviewerValidationPanel } from "@/components/cases/ReviewerValidationPanel";
import { SafetyFlagsPanel } from "@/components/cases/SafetyFlagsPanel";
import { TokenUsagePanel } from "@/components/cases/TokenUsagePanel";
import { HumanDecisionPanel } from "@/components/cases/HumanDecisionPanel";
import { AuditTrailPanel } from "@/components/cases/AuditTrailPanel";
import { HumanOverrideBanner } from "@/components/cases/HumanOverrideBanner";
import { StatusLifecyclePanel } from "@/components/cases/StatusLifecyclePanel";
import { AssignmentActionPanel } from "@/components/assignment/AssignmentActionPanel";
import { AssignmentHistoryPanel } from "@/components/assignment/AssignmentHistoryPanel";
import { AssignmentPriorityBadge } from "@/components/assignment/AssignmentPriorityBadge";
import { AssignmentStatusBadge } from "@/components/assignment/AssignmentStatusBadge";
import { SlaStatusBadge } from "@/components/assignment/SlaStatusBadge";
import { FeedbackButton } from "@/components/feedback/FeedbackButton";
import { getAssignmentHistory } from "@/services/assignmentService";
import { getAuditTrail } from "@/services/auditService";
import { runInvestigation } from "@/services/agentService";
import { getCaseDetail } from "@/services/caseService";
import { getCaseFeedback } from "@/services/feedbackService";
import { getCaseStatus } from "@/services/statusService";
import type { InvestigationPackage } from "@/types/agent.types";
import type { AuditTrail } from "@/types/audit.types";
import type { AssignmentHistoryRecord } from "@/types/assignment.types";
import type { CaseDetail } from "@/types/case.types";
import type { CaseStatusInfo } from "@/types/status.types";

type PageProps = {
  params: Promise<{ caseId: string }>;
};

export default function CaseDetailPage({ params }: PageProps) {
  const [caseId, setCaseId] = useState<string>("");
  const [caseDetail, setCaseDetail] = useState<CaseDetail | null>(null);
  const [auditTrail, setAuditTrail] = useState<AuditTrail | null>(null);
  const [assignmentHistory, setAssignmentHistory] = useState<AssignmentHistoryRecord[]>([]);
  const [statusInfo, setStatusInfo] = useState<CaseStatusInfo | null>(null);
  const [investigation, setInvestigation] = useState<InvestigationPackage | null>(null);
  const [feedbackCount, setFeedbackCount] = useState(0);
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
    const [detail, audit, status, history, feedback] = await Promise.all([
      getCaseDetail(caseId),
      getAuditTrail(caseId),
      getCaseStatus(caseId),
      getAssignmentHistory(caseId).catch(() => ({ history: [] })),
      getCaseFeedback(caseId).catch(() => ({ count: 0, feedback_records: [] }))
    ]);
    setCaseDetail(detail);
    setAuditTrail(audit);
    setStatusInfo(status);
    setAssignmentHistory(history.history);
    setFeedbackCount(feedback.count);
  }, [caseId]);

  useEffect(() => {
    if (!caseId) {
      return;
    }

    Promise.all([
      getCaseDetail(caseId),
      getAuditTrail(caseId),
      getCaseStatus(caseId),
      getAssignmentHistory(caseId).catch(() => ({ history: [] })),
      getCaseFeedback(caseId).catch(() => ({ count: 0, feedback_records: [] }))
    ])
      .then(([detail, audit, status, history, feedback]) => {
        setCaseDetail(detail);
        setAuditTrail(audit);
        setStatusInfo(status);
        setAssignmentHistory(history.history);
        setFeedbackCount(feedback.count);
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
                  <p className="muted">{feedbackCount} AI feedback records for this case</p>
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
              <section className="card">
                <div className="card-header">
                  <h3>Assignment Summary</h3>
                  <p>Current ownership, priority, and SLA posture.</p>
                </div>
                <div className="card-body meta-list">
                  <div className="meta-row"><span className="meta-label">Assigned To</span><span className="meta-value">{caseDetail.assignment?.assigned_to_name ?? caseDetail.assignment?.assigned_to ?? "Unassigned"}</span></div>
                  <div className="meta-row"><span className="meta-label">Team</span><span className="meta-value">{caseDetail.assignment?.assigned_team ?? "Fraud Operations"}</span></div>
                  <div className="meta-row"><span className="meta-label">Status</span><span className="meta-value"><AssignmentStatusBadge status={caseDetail.assignment?.assignment_status ?? "UNASSIGNED"} /></span></div>
                  <div className="meta-row"><span className="meta-label">Priority</span><span className="meta-value"><AssignmentPriorityBadge priority={caseDetail.assignment?.assignment_priority ?? "MEDIUM"} /></span></div>
                  <div className="meta-row"><span className="meta-label">SLA</span><span className="meta-value"><SlaStatusBadge status={caseDetail.assignment?.sla_status ?? "NOT_APPLICABLE"} /></span></div>
                </div>
              </section>
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
                  <AiProviderBadge
                    provider={investigation.ai_provider}
                    mode={investigation.ai_mode}
                    fallbackUsed={investigation.agent_trace.some((item) => JSON.stringify(item.output).includes("\"fallback_used\":true"))}
                  />
                  <RiskIndicatorPanel indicators={investigation.risk_indicators} title="AI Investigation Result" summary={investigation.investigation_summary} />
                  <div className="feedback-inline full-span">
                    <FeedbackButton caseId={caseId} targetType="INVESTIGATION_SUMMARY" actualAiRecommendation={investigation.investigation_summary.recommended_action} snapshot={investigation.investigation_summary as unknown as Record<string, unknown>} onSubmitted={refreshCase} />
                    <FeedbackButton caseId={caseId} targetType="AI_RECOMMENDATION" actualAiRecommendation={investigation.investigation_summary.recommended_action} snapshot={{ recommended_action: investigation.investigation_summary.recommended_action, confidence_level: investigation.investigation_summary.confidence_level }} onSubmitted={refreshCase} />
                    <FeedbackButton caseId={caseId} targetType="RISK_INDICATOR" actualAiRecommendation={investigation.investigation_summary.recommended_action} snapshot={{ risk_indicators: investigation.risk_indicators }} onSubmitted={refreshCase} />
                    <FeedbackButton caseId={caseId} targetType="OVERALL_AI_OUTPUT" actualAiRecommendation={investigation.investigation_summary.recommended_action} snapshot={{ recommended_action: investigation.investigation_summary.recommended_action, confidence_level: investigation.investigation_summary.confidence_level, policy_references: investigation.policy_references, safety_flags: investigation.safety_flags }} onSubmitted={refreshCase} />
                  </div>
                  <TokenUsagePanel usage={investigation.token_usage} latencyMs={investigation.latency_ms} />
                  <SafetyFlagsPanel flags={investigation.safety_flags} citationIssues={investigation.reviewer_validation.citation_issues} />
                  <AgentTracePanel trace={investigation.agent_trace} />
                  <div className="feedback-inline full-span">
                    <FeedbackButton caseId={caseId} targetType="AGENT_TRACE" actualAiRecommendation={investigation.investigation_summary.recommended_action} agentName="AgentOrchestrator" snapshot={{ agent_name: "AgentOrchestrator" }} onSubmitted={refreshCase} />
                  </div>
                  <PolicyReferencePanel references={investigation.policy_references} />
                  <div className="feedback-inline full-span">
                    <FeedbackButton caseId={caseId} targetType="POLICY_CITATION" actualAiRecommendation={investigation.investigation_summary.recommended_action} policySourceFile={investigation.policy_references[0]?.source_filename} policyChunkId={investigation.policy_references[0]?.chunk_id} snapshot={{ policy_references: investigation.policy_references }} onSubmitted={refreshCase} />
                  </div>
                  <SimilarCasesPanel cases={investigation.similar_cases} />
                  <div className="feedback-inline full-span">
                    <FeedbackButton caseId={caseId} targetType="SIMILAR_CASE_RETRIEVAL" actualAiRecommendation={investigation.investigation_summary.recommended_action} snapshot={{ similar_cases: investigation.similar_cases }} onSubmitted={refreshCase} />
                  </div>
                  <ReviewerValidationPanel validation={investigation.reviewer_validation} humanReviewRequired={investigation.human_review_required} />
                  <div className="feedback-inline full-span">
                    <FeedbackButton caseId={caseId} targetType="REVIEWER_VALIDATION" actualAiRecommendation={investigation.investigation_summary.recommended_action} snapshot={{ validation_result: investigation.reviewer_validation, human_review_required: investigation.human_review_required }} onSubmitted={refreshCase} />
                  </div>
                </>
              )}

              <HumanDecisionPanel
                caseId={caseId}
                currentStatus={caseDetail.current_status}
                aiRecommendation={caseDetail.ai_recommendation}
                onDecisionRecorded={handleDecisionRecorded}
              />
              <AssignmentActionPanel caseId={caseId} assignment={caseDetail.assignment} onDone={refreshCase} />
              <AssignmentHistoryPanel history={assignmentHistory} />
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
