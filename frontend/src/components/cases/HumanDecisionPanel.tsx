"use client";

import { FormEvent, useMemo, useState } from "react";
import { CardFrame } from "@/components/cases/CardFrame";
import { submitHumanReview } from "@/services/reviewService";
import type { HumanReviewDecision, ReasonCode, ReviewerRole } from "@/types/review.types";

const reviewerRoles: ReviewerRole[] = ["FRAUD_ANALYST", "FRAUD_MANAGER", "COMPLIANCE_OFFICER", "AUDITOR"];
const decisions: HumanReviewDecision[] = ["APPROVE", "HOLD", "ESCALATE", "REJECT"];
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
  const [decision, setDecision] = useState<HumanReviewDecision>("HOLD");
  const [reviewerRole, setReviewerRole] = useState<ReviewerRole>("FRAUD_ANALYST");
  const [reasonCode, setReasonCode] = useState<ReasonCode>("SUSPICIOUS_DEVICE");
  const [comment, setComment] = useState("");
  const [reviewedBy, setReviewedBy] = useState("");
  const [evidenceAcknowledged, setEvidenceAcknowledged] = useState(false);
  const [policyAcknowledged, setPolicyAcknowledged] = useState(false);
  const [overrideReason, setOverrideReason] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isPendingReview = currentStatus === "PENDING_HUMAN_REVIEW";
  const isOverride = Boolean(aiRecommendation && aiRecommendation !== decision);
  const validationErrors = useMemo(() => {
    const errors: string[] = [];
    if (!reviewedBy.trim()) errors.push("Reviewer name is required.");
    if (reviewerRole === "AUDITOR") errors.push("AUDITOR role is view-only and cannot submit decisions.");
    if (comment.trim().length < 10) errors.push("Comment must be at least 10 characters.");
    if (!evidenceAcknowledged) errors.push("Evidence acknowledgement is required.");
    if (!policyAcknowledged) errors.push("Policy acknowledgement is required.");
    if (isOverride && !overrideReason.trim()) errors.push("Override reason is required when decision differs from AI recommendation.");
    return errors;
  }, [comment, evidenceAcknowledged, isOverride, overrideReason, policyAcknowledged, reviewedBy, reviewerRole]);

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
      setMessage(`${response.message}. New status: ${response.new_status}`);
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

  return (
    <CardFrame title="Human Decision Panel" subtitle="Human review is required before any final case action is accepted.">
      <form className="form-grid" onSubmit={handleSubmit}>
        <div className="message">
          AI recommendation: {aiRecommendation ?? "Not available"}
        </div>
        <div className="field">
          <label htmlFor="decision">Decision</label>
          <select id="decision" value={decision} onChange={(event) => setDecision(event.target.value as HumanReviewDecision)}>
            {decisions.map((item) => <option value={item} key={item}>{item}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="reviewer_role">Reviewer role</label>
          <select id="reviewer_role" value={reviewerRole} onChange={(event) => setReviewerRole(event.target.value as ReviewerRole)}>
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
          <div className="field">
            <label htmlFor="override_reason">Override reason</label>
            <textarea id="override_reason" value={overrideReason} onChange={(event) => setOverrideReason(event.target.value)} placeholder="Explain why the human decision differs from AI recommendation" />
          </div>
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
