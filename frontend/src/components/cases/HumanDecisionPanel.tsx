"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { decisionOptionsByRole } from "@/auth/authConfig";
import { useAuth } from "@/auth/useAuth";
import { CardFrame } from "@/components/cases/CardFrame";
import { submitHumanReview } from "@/services/reviewService";
import type { HumanReviewDecision, ReasonCode, ReviewerRole } from "@/types/review.types";

const reviewerRoles: ReviewerRole[] = ["FRAUD_ANALYST", "FRAUD_MANAGER", "COMPLIANCE_OFFICER", "AUDITOR"];
const reasonCodes: ReasonCode[] = [
  "CUSTOMER_CONFIRMED",
  "SUSPICIOUS_DEVICE",
  "NEW_BENEFICIARY_RISK",
  "HIGH_VALUE_TRANSFER",
  "POLICY_THRESHOLD_BREACH",
  "INSUFFICIENT_EVIDENCE",
  "FALSE_POSITIVE",
  "ESCALATE_TO_AML"
];

type HumanDecisionPanelProps = {
  caseId: string;
  currentStatus: string;
  aiRecommendation: string | null;
  onDecisionRecorded: () => Promise<void>;
};

export function HumanDecisionPanel({ caseId, currentStatus, aiRecommendation, onDecisionRecorded }: HumanDecisionPanelProps) {
  const { user } = useAuth();
  const allowedDecisions = useMemo(
    () => (user ? decisionOptionsByRole[user.role] : ["HOLD"]) as HumanReviewDecision[],
    [user]
  );
  const [decision, setDecision] = useState<HumanReviewDecision>(allowedDecisions[0] ?? "HOLD");
  const [reviewerRole, setReviewerRole] = useState<ReviewerRole>((user?.role as ReviewerRole | undefined) ?? "FRAUD_ANALYST");
  const [reasonCode, setReasonCode] = useState<ReasonCode>("SUSPICIOUS_DEVICE");
  const [comment, setComment] = useState("");
  const [reviewedBy, setReviewedBy] = useState("");
  const [evidenceAcknowledged, setEvidenceAcknowledged] = useState(false);
  const [policyAcknowledged, setPolicyAcknowledged] = useState(false);
  const [overrideReason, setOverrideReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    if (!user) return;
    const updateRoles = () => {
      if (mounted) {
        setReviewerRole(user.role as ReviewerRole);
        setReviewedBy(user.user_id);
        setDecision((prev) => !allowedDecisions.includes(prev) && allowedDecisions[0] ? allowedDecisions[0] : prev);
      }
    };
    updateRoles();
    return () => { mounted = false; };
  }, [allowedDecisions, user]);

  const isPendingReview = currentStatus === "PENDING_HUMAN_REVIEW";
  const isAuditor = user?.role === "AUDITOR";
  const isOverride = Boolean(aiRecommendation && aiRecommendation !== decision);
  const hasAiRecommendation = Boolean(aiRecommendation);
  const validationErrors = useMemo(() => {
    const errors: string[] = [];
    if (!reviewedBy.trim()) errors.push("Reviewer name is required.");
    if (isAuditor || allowedDecisions.length === 0) errors.push("Auditor role can view the case but cannot submit a decision.");
    if (comment.trim().length < 10) errors.push("Comment must be at least 10 characters.");
    if (!evidenceAcknowledged) errors.push("Evidence acknowledgement is required.");
    if (!policyAcknowledged) errors.push("Policy acknowledgement is required.");
    if (isOverride && overrideReason.trim().length < 10) errors.push("Override reason must be at least 10 characters when decision differs from AI recommendation.");
    return errors;
  }, [allowedDecisions.length, comment, evidenceAcknowledged, isAuditor, isOverride, overrideReason, policyAcknowledged, reviewedBy]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (validationErrors.length > 0) {
      setError(validationErrors.join(" "));
      return;
    }

    setSubmitting(true);
    setMessage(null);
    setError(null);

    try {
      const response = await submitHumanReview(caseId, {
        decision,
        comment,
        reviewed_by: reviewedBy,
        reviewer_role: reviewerRole,
        reason_code: reasonCode,
        evidence_acknowledged: evidenceAcknowledged,
        policy_acknowledged: policyAcknowledged,
        override_reason: isOverride ? overrideReason : undefined
      });
      setMessage(
        response.human_override
          ? `${response.message}. Human override recorded: ${response.ai_recommendation} -> ${response.human_decision}.`
          : `${response.message}. Override status: ${response.override_comparison_status}. New status: ${response.new_status}`
      );
      await onDecisionRecorded();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  if (!isPendingReview) {
    return (
      <CardFrame title="Human Decision Panel" subtitle="Final decisions are available only during pending human review.">
        <div className="message">
          Current status is {currentStatus}. Decision submission is disabled until the case is pending human review.
        </div>
      </CardFrame>
    );
  }

  if (isAuditor) {
    return (
      <CardFrame title="Human Decision Panel" subtitle="Decision submission is restricted by role.">
        <div className="message">Auditor role can view the case but cannot submit a decision.</div>
      </CardFrame>
    );
  }

  return (
    <CardFrame title="Human Decision Panel" subtitle="Human review is required before any final case action is accepted.">
      <form className="form-grid" onSubmit={handleSubmit}>
        <div className="message">
          AI recommendation: {aiRecommendation ?? "Not available"}
        </div>
        {!hasAiRecommendation && (
          <div className="message">
            AI recommendation is not available. Override comparison will not be applied.
          </div>
        )}
        <div className="field">
          <label htmlFor="decision">Decision</label>
          <select id="decision" value={decision} onChange={(event) => setDecision(event.target.value as HumanReviewDecision)}>
            {allowedDecisions.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="reviewer_role">Reviewer role</label>
          <select id="reviewer_role" value={reviewerRole} onChange={(event) => setReviewerRole(event.target.value as ReviewerRole)} disabled>
            {reviewerRoles.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="reviewed_by">Reviewer name</label>
          <input id="reviewed_by" value={reviewedBy} onChange={(event) => setReviewedBy(event.target.value)} placeholder="synthetic.reviewer" />
        </div>
        <div className="field">
          <label htmlFor="reason_code">Reason code</label>
          <select id="reason_code" value={reasonCode} onChange={(event) => setReasonCode(event.target.value as ReasonCode)}>
            {reasonCodes.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="comment">Comment</label>
          <textarea id="comment" value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Add review rationale" />
        </div>
        <label className="checkbox-row">
          <input type="checkbox" checked={evidenceAcknowledged} onChange={(event) => setEvidenceAcknowledged(event.target.checked)} />
          I acknowledge the evidence package.
        </label>
        <label className="checkbox-row">
          <input type="checkbox" checked={policyAcknowledged} onChange={(event) => setPolicyAcknowledged(event.target.checked)} />
          I acknowledge the applicable policy references.
        </label>
        {isOverride && (
          <>
            <div className="message warning">
              You are overriding the AI recommendation.
            </div>
            <div className="field">
              <label htmlFor="override_reason">Override reason</label>
              <textarea id="override_reason" value={overrideReason} onChange={(event) => setOverrideReason(event.target.value)} placeholder="Explain why the human decision differs from AI recommendation" />
            </div>
          </>
        )}
        {validationErrors.length > 0 && <div className="message error">{validationErrors.join(" ")}</div>}
        {message && <div className="message success">{message}</div>}
        {error && <div className="message error">{error}</div>}
        <button className="button" type="submit" disabled={submitting || validationErrors.length > 0}>
          {submitting ? "Submitting Review" : "Submit Human Review"}
        </button>
      </form>
    </CardFrame>
  );
}
