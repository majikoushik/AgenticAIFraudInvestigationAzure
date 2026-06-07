import type { TokenUsageSummary } from "@/types/cost.types";
import { formatTokens } from "@/components/cost/costFormat";

export function TokenUsagePanel({ usage }: { usage: TokenUsageSummary }) {
  return (
    <section className="panel">
      <h2>Token Usage</h2>
      <div className="stack">
        <div className="row"><span>Prompt tokens</span><strong>{formatTokens(usage.total_prompt_tokens)}</strong></div>
        <div className="row"><span>Completion tokens</span><strong>{formatTokens(usage.total_completion_tokens)}</strong></div>
        <div className="row"><span>Total tokens</span><strong>{formatTokens(usage.total_tokens)}</strong></div>
      </div>
      <h3>By provider</h3>
      {Object.entries(usage.by_provider).map(([name, value]) => <div className="row" key={name}><span>{name}</span><strong>{formatTokens(value)}</strong></div>)}
      <h3>By model</h3>
      {Object.entries(usage.by_model).map(([name, value]) => <div className="row" key={name}><span>{name}</span><strong>{formatTokens(value)}</strong></div>)}
    </section>
  );
}
