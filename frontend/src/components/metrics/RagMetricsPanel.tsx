import { CardFrame } from "@/components/cases/CardFrame";
import { entries, formatPercent } from "@/components/metrics/metricsFormat";
import type { PolicyCitationMetrics, RagRetrievalMetrics } from "@/types/metrics.types";

type RagMetricsPanelProps = {
  rag: RagRetrievalMetrics;
  policy: PolicyCitationMetrics;
};

export function RagMetricsPanel({ rag, policy }: RagMetricsPanelProps) {
  return (
    <CardFrame title="RAG and Policy Grounding" subtitle="Retrieval success and policy reference coverage.">
      <div className="facts-grid">
        <div><span className="label">Retrievals</span><strong>{rag.total_rag_retrievals}</strong></div>
        <div><span className="label">RAG failures</span><strong>{rag.rag_failure_count}</strong></div>
        <div><span className="label">RAG failure rate</span><strong>{formatPercent(rag.rag_failure_rate_percentage)}</strong></div>
        <div><span className="label">Avg result count</span><strong>{rag.average_result_count.toFixed(1)}</strong></div>
        <div><span className="label">Policy reference rate</span><strong>{formatPercent(policy.policy_reference_rate_percentage)}</strong></div>
        <div><span className="label">Cases without policies</span><strong>{policy.cases_without_policy_references}</strong></div>
      </div>
      <div className="two-column-panel">
        <List title="Retrieval modes" items={entries(rag.retrieval_count_by_mode).map(([name, count]) => ({ name, count }))} />
        <List title="Top policy sources" items={policy.top_policy_sources.length ? policy.top_policy_sources : rag.top_retrieved_sources} />
      </div>
    </CardFrame>
  );
}

function List({ title, items }: { title: string; items: Array<{ name: string; count: number }> }) {
  return (
    <div>
      <h4>{title}</h4>
      {items.length === 0 ? <div className="empty-state">No records yet.</div> : (
        <table className="table">
          <thead><tr><th>Name</th><th>Count</th></tr></thead>
          <tbody>{items.map((item) => <tr key={item.name}><td>{item.name}</td><td>{item.count}</td></tr>)}</tbody>
        </table>
      )}
    </div>
  );
}
