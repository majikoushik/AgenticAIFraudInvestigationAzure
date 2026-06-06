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

Decision request body:

```json
{
  "decision": "hold",
  "comment": "Synthetic review requires additional verification.",
  "reviewed_by": "synthetic.reviewer"
}
```

Allowed decisions are `approve`, `hold`, `escalate`, and `reject`.
