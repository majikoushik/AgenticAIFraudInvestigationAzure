import { CardFrame } from "@/components/cases/CardFrame";
import type { PolicyReference } from "@/types/agent.types";

type PolicyReferencePanelProps = {
  references: PolicyReference[];
};

export function PolicyReferencePanel({ references }: PolicyReferencePanelProps) {
  return (
    <CardFrame title="Policy References" subtitle="Local markdown policy snippets returned by keyword RAG.">
      {references.length === 0 ? (
        <div className="empty-state">No policy references matched this case.</div>
      ) : (
        <div className="panel-list">
          {references.map((reference) => (
            <div className="panel-item" key={`${reference.source_filename}-${reference.matched_section}`}>
              <h4>{reference.title}</h4>
              <p><strong>{reference.matched_section}</strong> from {reference.source_filename}</p>
              <p>{reference.snippet}</p>
            </div>
          ))}
        </div>
      )}
    </CardFrame>
  );
}
