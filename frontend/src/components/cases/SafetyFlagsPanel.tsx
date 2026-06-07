import { CardFrame } from "@/components/cases/CardFrame";

type SafetyFlagsPanelProps = {
  flags: string[];
  citationIssues?: unknown[];
};

export function SafetyFlagsPanel({ flags, citationIssues = [] }: SafetyFlagsPanelProps) {
  return (
    <CardFrame title="Safety Flags" subtitle="Backend guardrail and citation validation results.">
      {flags.length === 0 && citationIssues.length === 0 ? (
        <div className="empty-state">No safety flags reported.</div>
      ) : (
        <div className="panel-list">
          {flags.map((flag) => (
            <div className="panel-item" key={flag}>{flag}</div>
          ))}
          {citationIssues.map((issue, index) => (
            <div className="panel-item" key={`citation-${index}`}>Citation issue: {JSON.stringify(issue)}</div>
          ))}
        </div>
      )}
    </CardFrame>
  );
}
