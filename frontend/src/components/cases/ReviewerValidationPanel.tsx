import { CardFrame } from "@/components/cases/CardFrame";
import type { ReviewerValidation } from "@/types/agent.types";

type ReviewerValidationPanelProps = {
  validation: ReviewerValidation;
  humanReviewRequired: boolean;
};

export function ReviewerValidationPanel({ validation, humanReviewRequired }: ReviewerValidationPanelProps) {
  return (
    <CardFrame title="Reviewer Validation" subtitle="Evidence support and human-review guardrails.">
      <div className="stack">
        <div className={validation.is_evidence_supported ? "message success" : "message error"}>
          {validation.is_evidence_supported ? "Recommendation is evidence-supported." : "Unsupported claims were found."}
        </div>
        <div className="panel-item">
          <h4>Human review</h4>
          <p>{humanReviewRequired || validation.human_review_required ? "Required before high-impact action." : "Not required."}</p>
          <p>Policy alignment: {validation.policy_alignment ?? "UNKNOWN"}</p>
        </div>
        {validation.citation_issues && validation.citation_issues.length > 0 && (
          <div className="panel-item">
            <h4>Citation issues</h4>
            <pre className="code-block">{JSON.stringify(validation.citation_issues, null, 2)}</pre>
          </div>
        )}
        {validation.unsupported_claims.length > 0 && (
          <div className="panel-item">
            <h4>Unsupported claims</h4>
            <p>{validation.unsupported_claims.join(" ")}</p>
          </div>
        )}
        <div className="panel-item">
          <h4>Review notes</h4>
          <p>{validation.review_notes.join(" ")}</p>
        </div>
      </div>
    </CardFrame>
  );
}
