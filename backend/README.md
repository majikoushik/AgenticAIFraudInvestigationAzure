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
- `GET /api/v1/rag/policies/search?query=...`: search local or Azure AI Search-backed policy RAG.
- `POST /api/v1/cases/{case_id}/review`: submit human review decision with role, reason, acknowledgements, and override tracking.
- `POST /api/v1/cases/{case_id}/close`: close an approved, held, escalated, or rejected case.
- `GET /api/v1/cases/{case_id}/review-options?reviewer_role=FRAUD_ANALYST`: return allowed decisions and reason codes.
- `GET /api/v1/cases/{case_id}/status`: return current status, metadata, and allowed next statuses.
- `PATCH /api/v1/cases/{case_id}/status`: perform a backend-validated status transition and write an audit event.
- `GET /api/v1/audit/search`: search local audit events by case, type, actor, role, or date range.
- `GET /api/v1/audit/event-types`: list supported audit event types and categories.
- `GET /api/v1/audit/summary`: aggregate local audit events by category and type.

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

## Local Audit Storage

Audit events are stored in `data/synthetic/audit_events.json` for the MVP. The audit service writes structured events through `AuditRepository`, using a temp-file replace pattern and sanitized metadata.

To reset local audit data:

```json
[]
```
