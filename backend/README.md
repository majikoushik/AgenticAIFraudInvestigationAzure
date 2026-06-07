# Backend

FastAPI service for fraud investigation APIs.

## Responsibilities

- API endpoints for health, fraud cases, alerts, evidence, decisions, and audit trail
- Pydantic request and response validation
- Repository layer for local synthetic data during MVP development
- Service layer ready for future Azure integrations

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "fraud-investigation-backend"
}
```

## MVP API Endpoints

Swagger UI is available at `http://localhost:8000/docs`.

- `GET /health`: backend health check.
- `GET /api/v1/cases`: list synthetic fraud alert cases.
- `GET /api/v1/cases/{case_id}`: get detailed case evidence, including masked customer account number, suspicious transaction, beneficiary, device, risk indicators, historical cases, and current status.
- `POST /api/v1/cases/{case_id}/decision`: record a human investigator decision.
- `GET /api/v1/cases/{case_id}/audit`: return in-memory audit entries for the case.
- `POST /api/v1/cases/{case_id}/investigate`: run the local deterministic agent orchestration and policy RAG simulation.
- `GET /api/v1/agents/config`: return safe agent runtime configuration without API keys or secrets.
- `GET /api/v1/agents/provider`: return active AI provider, fallback, JSON mode, logging flags, and human-review requirement without secrets.
- `GET /api/v1/rag/policies/search?query=...`: search local or Azure AI Search-backed policy RAG.
- `GET /api/v1/rag/health`: return local/Azure RAG configuration status without secrets.
- `POST /api/v1/rag/search/policies`: search policy references with citation metadata.
- `POST /api/v1/rag/search/historical-cases`: search similar synthetic historical case references.
- `POST /api/v1/rag/search/case-evidence`: search synthetic case evidence records.
- `POST /api/v1/rag/search/all`: search policy, historical case, and case evidence indexes together.
- `POST /api/v1/cases/{case_id}/review`: submit human review decision with role, reason, acknowledgements, and override tracking.
- `GET /api/v1/cases/{case_id}/override-summary`: return latest AI-vs-human override comparison for a case.
- `POST /api/v1/cases/{case_id}/close`: close an approved, held, escalated, or rejected case.
- `GET /api/v1/cases/{case_id}/review-options?reviewer_role=FRAUD_ANALYST`: return allowed decisions and reason codes.
- `GET /api/v1/cases/{case_id}/status`: return current status, metadata, and allowed next statuses.
- `PATCH /api/v1/cases/{case_id}/status`: perform a backend-validated status transition and write an audit event.
- `GET /api/v1/audit/search`: search local audit events by case, type, actor, role, or date range.
- `GET /api/v1/audit/event-types`: list supported audit event types and categories.
- `GET /api/v1/audit/summary`: aggregate local audit events by category and type.
- `GET /api/v1/metrics/summary`: return all evaluation dashboard metric groups.
- `GET /api/v1/metrics/case-status`: return case lifecycle status metrics.
- `GET /api/v1/metrics/ai-vs-human`: return AI recommendation, human decision, and override metrics.
- `GET /api/v1/metrics/operations`: return investigation timing, review timing, agent, and RAG metrics.
- `GET /api/v1/metrics/audit`: return audit event distribution metrics.
- `GET /api/v1/metrics/timeseries`: return simple daily counts.
- `GET /api/v1/auth/mode`: return active auth mode.
- `GET /api/v1/auth/me`: return authenticated user context.
- `GET /api/v1/auth/permissions`: return permissions for the authenticated user.
- `GET /api/v1/health/details`: return protected secret-safe health and observability details.
- `GET /api/v1/observability/events`: return recent sanitized local telemetry events for admin users.

Decision request body:

```json
{
  "decision": "hold",
  "comment": "Synthetic review requires additional verification.",
  "reviewed_by": "synthetic.reviewer"
}
```

Allowed decisions are `approve`, `hold`, `escalate`, and `reject`.

## Human Review Example

```json
{
  "decision": "HOLD",
  "comment": "Synthetic suspicious device review requires additional verification.",
  "reviewed_by": "synthetic.reviewer",
  "reviewer_role": "FRAUD_ANALYST",
  "reason_code": "SUSPICIOUS_DEVICE",
  "evidence_acknowledged": true,
  "policy_acknowledged": true
}
```

The backend enforces role permissions, required acknowledgements, override reason requirements, and status transitions.

Override review example:

```json
{
  "decision": "ESCALATE",
  "comment": "Synthetic suspicious beneficiary review requires escalation.",
  "reviewed_by": "synthetic.reviewer",
  "reviewer_role": "FRAUD_ANALYST",
  "reason_code": "SUSPICIOUS_DEVICE",
  "evidence_acknowledged": true,
  "policy_acknowledged": true,
  "override_reason": "Beneficiary is linked to multiple suspicious synthetic cases."
}
```

Review responses include:

```json
{
  "case_id": "case-001",
  "decision": "ESCALATE",
  "ai_recommendation": "HOLD",
  "human_decision": "ESCALATE",
  "human_override": true,
  "override_reason": "Beneficiary is linked to multiple suspicious synthetic cases.",
  "override_comparison_status": "OVERRIDDEN",
  "message": "Human review submitted successfully"
}
```

Override summary response:

```json
{
  "case_id": "case-001",
  "has_override": true,
  "ai_recommendation": "HOLD",
  "human_decision": "ESCALATE",
  "override_reason": "Beneficiary is linked to multiple suspicious synthetic cases.",
  "override_detected_at": "2026-06-06T11:30:00Z",
  "override_detected_by": "synthetic.reviewer",
  "override_comparison_status": "OVERRIDDEN"
}
```

## Local Audit Storage

Audit events are stored in `data/synthetic/audit_events.json` for the MVP. The audit service writes structured events through `AuditRepository`, using a temp-file replace pattern and sanitized metadata.

To reset local audit data:

```json
[]
```

## Evaluation Metrics

Metrics are calculated locally from `data/synthetic/fraud_alerts.json` and `data/synthetic/audit_events.json`. The service is centralized in `app/services/metrics_service.py` so the MVP can later move the same calculations to Cosmos DB, Azure Monitor, Log Analytics, or Power BI.

## Authentication

Local development uses `AUTH_MODE=local`. The backend accepts development-only demo headers:

```text
X-Demo-User=fraud_analyst_01
X-Demo-Role=FRAUD_ANALYST
X-Demo-Email=fraud_analyst_01@example.com
```

For Entra ID mode, set `AUTH_MODE=entra` and configure `ENTRA_TENANT_ID`, `ENTRA_CLIENT_ID`, `ENTRA_API_AUDIENCE`, and `ENTRA_AUTHORITY`. The backend validates Bearer JWTs and enforces role-based permissions.

## AI Provider Modes

Local deterministic mode is default:

```env
AI_PROVIDER=local
```

Azure OpenAI mode is backend-only and must use secure configuration:

```env
AI_PROVIDER=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=<secure value>
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
LLM_LOG_PROMPTS=false
LLM_LOG_RESPONSES=false
```

Investigation responses include provider, mode, token usage, latency, citations, safety flags, validation result, and `human_review_required=true`.

## Observability

Local telemetry is enabled by default and writes sanitized events to `data/synthetic/telemetry_events.json` when Application Insights is not configured.

```env
OBSERVABILITY_ENABLED=true
OBSERVABILITY_MODE=local
APPLICATIONINSIGHTS_CONNECTION_STRING=
LOG_FORMAT=json
TELEMETRY_LOG_PROMPTS=false
TELEMETRY_LOG_RESPONSES=false
TELEMETRY_LOG_PII=false
```

For Azure Monitor, set `APPLICATIONINSIGHTS_CONNECTION_STRING` through Key Vault or secure app configuration. Do not commit it.
