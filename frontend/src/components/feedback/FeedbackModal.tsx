"use client";

import { useState } from "react";
import { FeedbackIssueTypeSelector } from "@/components/feedback/FeedbackIssueTypeSelector";
import { FeedbackRatingSelector } from "@/components/feedback/FeedbackRatingSelector";
import { submitFeedback } from "@/services/feedbackService";
import type { FeedbackIssueType, FeedbackRating, FeedbackSeverity, FeedbackTargetType } from "@/types/feedback.types";

type Props = {
  caseId: string;
  targetType: FeedbackTargetType;
  actualAiRecommendation?: string | null;
  humanDecision?: string | null;
  agentName?: string | null;
  policySourceFile?: string | null;
  policyChunkId?: string | null;
  snapshot?: Record<string, unknown>;
  onClose: () => void;
  onSubmitted?: () => void;
};

export function FeedbackModal(props: Props) {
  const [rating, setRating] = useState<FeedbackRating>("ACCEPTABLE");
  const [severity, setSeverity] = useState<FeedbackSeverity>("MEDIUM");
  const [issueTypes, setIssueTypes] = useState<FeedbackIssueType[]>([]);
  const [comment, setComment] = useState("");
  const [suggestedCorrection, setSuggestedCorrection] = useState("");
  const [expectedRecommendation, setExpectedRecommendation] = useState("");
  const [policySourceFile, setPolicySourceFile] = useState(props.policySourceFile ?? "");
  const [policyChunkId, setPolicyChunkId] = useState(props.policyChunkId ?? "");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const negative = rating === "POOR" || rating === "VERY_POOR";
  const citationIssue = issueTypes.includes("WRONG_POLICY_CITATION") || issueTypes.includes("MISSING_POLICY_CITATION");

  async function handleSubmit() {
    if (negative && comment.trim().length < 10) {
      setError("Negative feedback requires a comment of at least 10 characters.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await submitFeedback({
        case_id: props.caseId,
        target_type: props.targetType,
        rating,
        severity,
        issue_types: issueTypes,
        comment,
        suggested_correction: suggestedCorrection || null,
        expected_recommendation: expectedRecommendation || null,
        actual_ai_recommendation: props.actualAiRecommendation ?? null,
        human_decision: props.humanDecision ?? null,
        policy_source_file: policySourceFile || null,
        policy_chunk_id: policyChunkId || null,
        agent_name: props.agentName ?? null,
        sanitized_ai_output_snapshot: props.snapshot ?? {},
        metadata: { source: "case_detail" }
      });
      props.onSubmitted?.();
      props.onClose();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true">
      <div className="modal-card feedback-modal">
        <div className="card-header">
          <h3>AI Feedback</h3>
          <p>{props.targetType.replaceAll("_", " ")}</p>
        </div>
        <div className="card-body feedback-form">
          {error && <div className="error-inline">{error}</div>}
          <label>Rating<FeedbackRatingSelector value={rating} onChange={setRating} /></label>
          <label>Severity
            <select value={severity} onChange={(event) => setSeverity(event.target.value as FeedbackSeverity)}>
              {["LOW", "MEDIUM", "HIGH", "CRITICAL"].map((item) => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label>Issue Types<FeedbackIssueTypeSelector value={issueTypes} onChange={setIssueTypes} /></label>
          <label>Comment<textarea value={comment} onChange={(event) => setComment(event.target.value)} rows={4} /></label>
          <label>Suggested Correction<textarea value={suggestedCorrection} onChange={(event) => setSuggestedCorrection(event.target.value)} rows={3} /></label>
          {props.targetType === "AI_RECOMMENDATION" && <label>Expected Recommendation<input value={expectedRecommendation} onChange={(event) => setExpectedRecommendation(event.target.value)} placeholder="ESCALATE" /></label>}
          {citationIssue && (
            <div className="feedback-two-col">
              <label>Policy Source<input value={policySourceFile} onChange={(event) => setPolicySourceFile(event.target.value)} /></label>
              <label>Policy Chunk<input value={policyChunkId} onChange={(event) => setPolicyChunkId(event.target.value)} /></label>
            </div>
          )}
        </div>
        <div className="modal-actions">
          <button className="button secondary" onClick={props.onClose} disabled={saving}>Cancel</button>
          <button className="button" onClick={handleSubmit} disabled={saving}>{saving ? "Submitting" : "Submit Feedback"}</button>
        </div>
      </div>
    </div>
  );
}
