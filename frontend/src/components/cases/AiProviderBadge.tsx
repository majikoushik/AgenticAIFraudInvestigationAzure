type AiProviderBadgeProps = {
  provider: string;
  mode: string;
  fallbackUsed?: boolean;
};

const labels: Record<string, string> = {
  local: "Local Deterministic",
  azure_openai: "Azure OpenAI",
  foundry_agent_service: "Azure AI Foundry Agent Service",
};

export function AiProviderBadge({ provider, mode, fallbackUsed = false }: AiProviderBadgeProps) {
  return (
    <div className="card full-span">
      <div className="card-body provider-row">
        <div>
          <span className="label">AI Provider</span>
          <strong>{labels[provider] ?? provider}</strong>
          <p>{mode === "production" ? "Production AI mode" : "Local deterministic mode"}</p>
        </div>
        <span className="badge risk-medium">Human review required</span>
        {fallbackUsed && <span className="badge risk-low">Fallback mode used due to provider unavailability.</span>}
      </div>
    </div>
  );
}
