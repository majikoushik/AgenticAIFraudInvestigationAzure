# Agents

Python agent layer for the Agentic AI Fraud Investigation MVP.

The workflow runs in local deterministic mode by default and can optionally use Azure OpenAI for prompt-ready reasoning, summarization, and reviewer validation.

## Modes

### Local Deterministic Mode

Default mode. No Azure credentials are required and no external API calls are made.

```env
AI_PROVIDER=local
AI_PROVIDER_ALLOW_FALLBACK=true
```

### Azure OpenAI Mode

Enable Azure OpenAI only when credentials are supplied through environment variables or secure runtime configuration.

```env
AI_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=<secure value>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
LLM_ENABLE_JSON_MODE=true
LLM_LOG_PROMPTS=false
LLM_LOG_RESPONSES=false
```

Do not commit API keys or secrets.

### Azure AI Foundry Placeholder Mode

The Foundry client implements the shared interface but is intentionally a placeholder for this MVP.

```env
AI_PROVIDER=foundry_agent_service
USE_AZURE_AI_FOUNDRY_AGENT_SERVICE=true
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com
AZURE_AI_FOUNDRY_AGENT_ID=<agent-id>
```

The shared client contract returns provider, model, content, parsed JSON, token usage, latency, finish reason, and structured error metadata.

## Token Usage

The LLM helpers estimate token usage with a local character-count fallback when provider usage metadata is unavailable. The backend persists token and estimated cost records after investigations through `TokenUsageService`. Raw prompts and raw responses are not stored.

## Agent Flow

The default orchestrator runs:

- Case intake
- Customer profile analysis
- Transaction pattern analysis
- Device and location analysis
- Beneficiary risk analysis
- Policy RAG
- Historical case retrieval
- Case summary
- Reviewer validation

## Safety Guardrails

`agents/safety/GuardrailEngine` enforces MVP safety checks:

- The AI must not accuse a customer directly.
- The AI must not recommend permanent account freeze without human review.
- The AI must not make decisions without evidence.
- Missing evidence must be marked clearly.
- Policy references should be cited when applicable.
- High-value transaction cases require human review.
- Prompt injection indicators are detected before LLM prompts are built.
- PII redaction is applied before Azure OpenAI calls.
- Invented citations are flagged.

## Testing

From the repository root:

```bash
python -m pytest agents/tests
```

## Observability

Agent telemetry is emitted through lightweight wrappers in `agents/observability/`. In backend runtime they reuse the backend telemetry client; outside backend runtime they safely no-op. Agent telemetry never logs full outputs, prompts, raw responses, or PII.

## Adding A New Agent

1. Add a class under `agents/agents/` extending `BaseAgent`.
2. Return plain JSON-serializable dictionaries.
3. Add the agent to `AgentRegistry`.
4. Add tests under `agents/tests/`.
5. Keep external calls behind client abstractions.
