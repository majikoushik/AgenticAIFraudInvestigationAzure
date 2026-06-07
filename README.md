# Agentic AI Fraud Investigation Azure

Production-style MVP skeleton for an Agentic AI Banking Fraud Investigation System on Azure.

The project demonstrates the shape of a banking fraud investigation platform without real customer data, real credentials, or external AI calls. The current MVP includes a runnable FastAPI backend health endpoint, a valid Next.js TypeScript frontend skeleton, local synthetic data, agent and RAG module placeholders, Azure Bicep placeholders, and an Azure DevOps pipeline placeholder.

## Architecture

- `frontend/`: Next.js TypeScript investigator dashboard shell.
- `backend/`: FastAPI API service for case and investigation workflows.
- `agents/`: Python agent orchestration structure for deterministic MVP agents.
- `rag/`: Local document ingestion and retrieval structure, future-ready for Azure AI Search.
- `data/synthetic/`: Synthetic customers, transactions, beneficiaries, devices, fraud alerts, and historical cases.
- `infra/bicep/`: Azure infrastructure placeholders.
- `pipelines/`: Azure DevOps pipeline placeholder.

## Local Setup

Prerequisites:

- Node.js 20+
- Python 3.11+
- Docker Desktop, optional but recommended

### Run With Docker Compose

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Backend health: `http://localhost:8000/health`

### Run Backend Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Frontend Locally

```bash
cd frontend
npm install
npm run dev
```

## Security Notes

- All data is synthetic.
- `.env.example` files contain placeholders only.
- No real banking data, secrets, or credentials should be committed.
- High-impact actions such as freezing accounts must require human review.

## Human Review Workflow

The MVP requires human review before final case actions. AI investigation moves a case through `AI_INVESTIGATION_IN_PROGRESS`, `AI_INVESTIGATION_COMPLETED`, and `PENDING_HUMAN_REVIEW`. A reviewer then submits `APPROVE`, `HOLD`, `ESCALATE`, or `REJECT` according to role permissions.

Details are documented in [docs/human-review-workflow.md](docs/human-review-workflow.md).

The backend-enforced status state machine is documented in [docs/case-status-lifecycle.md](docs/case-status-lifecycle.md).

The structured audit trail is documented in [docs/audit-trail.md](docs/audit-trail.md).

Human override tracking is documented in [docs/human-override-tracking.md](docs/human-override-tracking.md).

The evaluation metrics dashboard is documented in [docs/evaluation-metrics-dashboard.md](docs/evaluation-metrics-dashboard.md).

Microsoft Entra ID and local demo authentication are documented in [docs/entra-id-authentication.md](docs/entra-id-authentication.md).

Azure AI Search production RAG setup is documented in [docs/azure-ai-search-production-rag.md](docs/azure-ai-search-production-rag.md). The MVP remains local-first with deterministic keyword retrieval unless `USE_AZURE_SEARCH=true` and Azure Search settings are configured.

Local verification:

1. Start the backend and frontend with `start-local.bat`.
2. Open `http://localhost:3000/login` and select a demo role.
3. Open `http://localhost:3000/cases/case-001`.
4. Submit a human review as `FRAUD_ANALYST` with `HOLD`.
5. Confirm the audit trail records the authenticated actor and status change.
6. Submit `ESCALATE` on `case-001` with an override reason to verify the override banner and `HUMAN_OVERRIDE_DETECTED` audit event.
7. Open `http://localhost:3000/metrics` to review AI-human agreement, override rate, operational, RAG, agent, and audit metrics.

## Agent Runtime Modes

Local deterministic mode is the default and requires no Azure credentials:

```env
USE_AZURE_OPENAI=false
USE_AZURE_AI_FOUNDRY_AGENT_SERVICE=false
```

To enable Azure OpenAI mode, configure values through environment variables, Key Vault, or secure pipeline variables:

```env
USE_AZURE_OPENAI=true
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=<secure value>
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
```

Never commit API keys. The backend safe config endpoint at `/api/v1/agents/config` reports mode and deployment configuration status without returning secrets.

## Current MVP Scope

Implemented:

- Repository skeleton
- FastAPI health endpoint
- Next.js app shell
- Docker Compose wiring
- Azure DevOps pipeline placeholder
- Synthetic JSON seed files

Not implemented yet:

- Fraud case dashboard APIs
- Agent investigation workflow
- RAG retrieval logic
- Human review workflow
- Audit trail persistence
