import { CardFrame } from "@/components/cases/CardFrame";
import type { PolicyReference } from "@/types/agent.types";

type PolicyReferencePanelProps = {
  references: PolicyReference[];
};

export function PolicyReferencePanel({ references }: PolicyReferencePanelProps) {
  return (
    <CardFrame title="Policy References" subtitle="RAG policy snippets with source citation metadata.">
      {references.length === 0 ? (
        <div className="empty-state">No policy references matched this case.</div>
      ) : (
        <div className="panel-list">
          {references.map((reference) => (
            <div className="panel-item" key={`${reference.source_filename}-${reference.matched_section}-${reference.chunk_id ?? "snippet"}`}>
              <h4>{reference.title}</h4>
              <p>
                <strong>{reference.matched_section}</strong> from {reference.source_filename}
              </p>
              <p>{reference.snippet}</p>
              <div className="meta-row">
                <span>{reference.retrieval_mode ?? "local"}</span>
                {reference.chunk_id && <span>Chunk {reference.chunk_id}</span>}
                {typeof reference.score === "number" && <span>Score {reference.score.toFixed(2)}</span>}
                {typeof reference.reranker_score === "number" && reference.reranker_score > 0 && (
                  <span>Reranker {reference.reranker_score.toFixed(2)}</span>
                )}
              </div>
              {reference.citation && (
                <p className="caption">
                  Citation: {reference.citation.title ?? reference.title}
                  {reference.citation.section ? ` / ${reference.citation.section}` : ""}
                  {reference.citation.source ? ` / ${reference.citation.source}` : ""}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </CardFrame>
  );
}
