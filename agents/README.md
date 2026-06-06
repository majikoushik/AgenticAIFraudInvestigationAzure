# Agents

Python agent layer for the Agentic AI Fraud Investigation MVP.

The workflow runs in local deterministic mode by default and can optionally use Azure OpenAI for prompt-ready reasoning, summarization, and reviewer validation.

## Modes

### Local Deterministic Mode

Default mode. No Azure credentials are required and no external API calls are made.

```env
USE_AZURE_OPENAI=false
USE_AZURE_AI_FOUNDRY_AGENT_SERVICE=false
```

### Azure OpenAI Mode

Enable Azure OpenAI only when credentials are supplied through environment variables or secure runtime configuration.

```env
USE_AZURE_OPENAI=true
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=<secure value>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

Do not commit API keys or secrets.

### Azure AI Foundry Placeholder Mode

The Foundry client implements the shared interface but is intentionally a placeholder for this MVP.

```env
USE_AZURE_AI_FOUNDRY_AGENT_SERVICE=true
AZURE_AI_FOUNDRY_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com
AZURE_AI_FOUNDRY_AGENT_ID=<agent-id>
```

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

`GuardrailEngine` enforces MVP safety checks:

- The AI must not accuse a customer directly.
- The AI must not recommend permanent account freeze without human review.
- The AI must not make decisions without evidence.
- Missing evidence must be marked clearly.
- Policy references should be cited when applicable.
- High-value transaction cases require human review.

## Testing

From the repository root:

```bash
python -m pytest agents/tests
```

## Adding A New Agent

1. Add a class under `agents/agents/` extending `BaseAgent`.
2. Return plain JSON-serializable dictionaries.
3. Add the agent to `AgentRegistry`.
4. Add tests under `agents/tests/`.
5. Keep external calls behind client abstractions.
