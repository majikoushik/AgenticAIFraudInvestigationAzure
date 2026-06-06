import { CardFrame } from "@/components/cases/CardFrame";
import type { AgentTraceItem } from "@/types/agent.types";

type AgentTracePanelProps = {
  trace: AgentTraceItem[];
};

export function AgentTracePanel({ trace }: AgentTracePanelProps) {
  return (
    <CardFrame title="Agent Execution Trace" subtitle="Step-by-step deterministic agent outputs." fullSpan>
      <div className="panel-list">
        {trace.map((item, index) => (
          <div className="panel-item trace-item" key={`${item.agent}-${index}`}>
            <h4>{index + 1}. {item.agent}</h4>
            <pre className="code-block">{JSON.stringify(item.output, null, 2)}</pre>
          </div>
        ))}
      </div>
    </CardFrame>
  );
}
