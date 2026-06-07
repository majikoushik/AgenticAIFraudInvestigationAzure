# Azure OpenAI and Foundry Production Mode

This feature adds a controlled production AI provider layer for the fraud investigation agents while preserving local deterministic mode.

## Modes

- `AI_PROVIDER=local`: no external LLM calls. Rule-based agents and deterministic local LLM responses are used.
- `AI_PROVIDER=azure_openai`: Azure OpenAI is used for structured summaries and reviewer validation when configured.
- `AI_PROVIDER=foundry_agent_service`: Azure AI Foundry Agent Service-ready adapter. The MVP exposes the interface and configuration placeholders; live SDK calls are intentionally left as a future integration point.

`AI_PROVIDER_ALLOW_FALLBACK=true` lets production-like environments fall back to local mode if the requested provider is unavailable. Set it to `false` to fail fast on missing provider configuration.

## Environment

Required for Azure OpenAI mode:

```env
AI_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=<secure value>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_REQUEST_TIMEOUT_SECONDS=60
AZURE_OPENAI_MAX_RETRIES=3
AZURE_OPENAI_TEMPERATURE=0.2
AZURE_OPENAI_MAX_TOKENS=2000
```

Prompt and response logging default to false:

```env
LLM_LOG_PROMPTS=false
LLM_LOG_RESPONSES=false
```

Do not commit keys. Use Key Vault, pipeline secrets, or enterprise-approved configuration. Do not expose these values to the frontend.

## Architecture

The LLM abstraction lives under `agents/llm/`:

- `BaseLLMClient`: normalized response contract.
- `LocalLLMClient`: deterministic test and demo provider.
- `AzureOpenAIClient`: Azure OpenAI chat client with redaction, JSON mode, latency, token usage, and structured errors.
- `FoundryAgentClient`: Foundry Agent Service-ready placeholder adapter.
- `LLMClientFactory`: selects providers from environment.
- `LLMResponseParser`: parses and normalizes JSON output.

Safety modules live under `agents/safety/`:

- PII redaction
- Prompt injection detection
- Output validation
- Citation validation
- Recommendation policy enforcement
- Guardrail engine

## Guardrails

The backend remains the source of truth for safety:

- Human review is always required.
- The AI must not accuse customers directly.
- The AI must not freeze or permanently block accounts.
- Missing evidence must be marked.
- Citations must come from retrieved RAG references.
- Raw prompts and raw responses are not stored in audit logs.

## Audit

The orchestrator records safe provider metadata such as provider name, fallback setting, latency, token usage, validation status, and safety flag counts. It does not store raw prompts, raw model responses, API keys, JWTs, or full PII.

## Backend API

Provider status:

```http
GET /api/v1/agents/provider
```

Investigation responses include:

- `ai_provider`
- `ai_mode`
- `token_usage`
- `latency_ms`
- `citations`
- `safety_flags`
- `validation_result`
- `human_review_required`

## Frontend

The case detail page displays provider mode, token usage, latency, safety flags, reviewer validation, citation issues, and human review requirement. It does not display raw prompts or model responses.

## Local Verification

```bash
python -m pytest agents/tests
cd backend
python -m pytest tests
cd ../frontend
npm run build
```

## Foundry Readiness

`FoundryAgentClient` reads project endpoint, agent ID, connection name, and thread ID from environment variables. Live service calls should be added after SDK choice, identity strategy, and enterprise deployment patterns are finalized.

## Future Improvements

- Managed identity for Azure OpenAI where supported
- Key Vault secret references in Container Apps
- Azure AI Content Safety
- Prompt versioning
- Model evaluation pipeline
- A/B testing between deployments
- Online feedback loop
- Azure Monitor and Application Insights telemetry
