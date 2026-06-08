import type { FeedbackIssueType } from "@/types/feedback.types";

const issueTypes: FeedbackIssueType[] = [
  "INCORRECT_RECOMMENDATION",
  "MISSING_EVIDENCE",
  "UNSUPPORTED_CLAIM",
  "WRONG_POLICY_CITATION",
  "MISSING_POLICY_CITATION",
  "IRRELEVANT_SIMILAR_CASE",
  "MISSING_SIMILAR_CASE",
  "POOR_EXPLANATION",
  "TOO_VERBOSE",
  "TOO_SHORT",
  "HALLUCINATION_SUSPECTED",
  "SAFETY_CONCERN",
  "PII_CONCERN",
  "PROMPT_INJECTION_CONCERN",
  "OTHER"
];

export function FeedbackIssueTypeSelector({ value, onChange }: { value: FeedbackIssueType[]; onChange: (value: FeedbackIssueType[]) => void }) {
  function toggle(issue: FeedbackIssueType) {
    onChange(value.includes(issue) ? value.filter((item) => item !== issue) : [...value, issue]);
  }
  return (
    <div className="feedback-chip-grid">
      {issueTypes.map((issue) => (
        <label key={issue} className="feedback-chip">
          <input type="checkbox" checked={value.includes(issue)} onChange={() => toggle(issue)} />
          <span>{issue.replaceAll("_", " ")}</span>
        </label>
      ))}
    </div>
  );
}
