import { CardFrame } from "@/components/cases/CardFrame";
import type { TokenUsage } from "@/types/agent.types";

type TokenUsagePanelProps = {
  usage: TokenUsage;
  latencyMs: number;
};

export function TokenUsagePanel({ usage, latencyMs }: TokenUsagePanelProps) {
  return (
    <CardFrame title="AI Runtime" subtitle="Token and latency metadata returned by the backend.">
      <div className="meta-list">
        <div className="meta-row"><span className="meta-label">Prompt tokens</span><span className="meta-value">{usage.prompt_tokens}</span></div>
        <div className="meta-row"><span className="meta-label">Completion tokens</span><span className="meta-value">{usage.completion_tokens}</span></div>
        <div className="meta-row"><span className="meta-label">Total tokens</span><span className="meta-value">{usage.total_tokens}</span></div>
        <div className="meta-row"><span className="meta-label">LLM latency</span><span className="meta-value">{latencyMs.toFixed(2)} ms</span></div>
      </div>
    </CardFrame>
  );
}
