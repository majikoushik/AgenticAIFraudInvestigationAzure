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
- Retention defaults are placeholders and must be approved by legal/compliance before production use.

## Data Retention and Compliance

The MVP includes local JSON-backed retention policies, legal holds, dry-run retention scans, archive and purge execution frameworks, review queues, and sanitized compliance exports. Purge defaults to dry-run, active legal holds block purge, and compliance exports redact PII-like values while excluding raw prompts, raw model responses, secrets, and chain-of-thought.

See [docs/data-retention-compliance-policy.md](docs/data-retention-compliance-policy.md).

## Human Review Workflow

The MVP requires human review before final case actions. AI investigation moves a case through `AI_INVESTIGATION_IN_PROGRESS`, `AI_INVESTIGATION_COMPLETED`, and `PENDING_HUMAN_REVIEW`. A reviewer then submits `APPROVE`, `HOLD`, `ESCALATE`, or `REJECT` according to role permissions.

Details are documented in [docs/human-review-workflow.md](docs/human-review-workflow.md).

The backend-enforced status state machine is documented in [docs/case-status-lifecycle.md](docs/case-status-lifecycle.md).

The structured audit trail is documented in [docs/audit-trail.md](docs/audit-trail.md).

Human override tracking is documented in [docs/human-override-tracking.md](docs/human-override-tracking.md).

The evaluation metrics dashboard is documented in [docs/evaluation-metrics-dashboard.md](docs/evaluation-metrics-dashboard.md).

Microsoft Entra ID and local demo authentication are documented in [docs/entra-id-authentication.md](docs/entra-id-authentication.md).

Azure AI Search production RAG setup is documented in [docs/azure-ai-search-production-rag.md](docs/azure-ai-search-production-rag.md). The MVP remains local-first with deterministic keyword retrieval unless `USE_AZURE_SEARCH=true` and Azure Search settings are configured.

Azure OpenAI and Azure AI Foundry production mode is documented in [docs/azure-openai-foundry-production-mode.md](docs/azure-openai-foundry-production-mode.md). Local mode remains the default through `AI_PROVIDER=local`; Azure OpenAI mode is enabled only through backend/agent environment variables.

Production observability with local telemetry fallback and Azure Monitor-ready structure is documented in [docs/production-observability-monitoring.md](docs/production-observability-monitoring.md).

Alerting and incident response with local alert stores, runbooks, KQL placeholders, incident workflow, and admin-only APIs is documented in [docs/alerting-and-incident-response.md](docs/alerting-and-incident-response.md).

Cost monitoring and token usage dashboards are documented in [docs/cost-monitoring-token-usage-dashboard.md](docs/cost-monitoring-token-usage-dashboard.md). Cost estimates default to zero until pricing environment variables are configured.

The safe Admin Configuration Panel is documented in [docs/admin-configuration-panel.md](docs/admin-configuration-panel.md). It manages only allow-listed non-secret runtime settings and feature flags.

Case assignment and investigator queues are documented in [docs/case-assignment-investigator-queue.md](docs/case-assignment-investigator-queue.md). The MVP includes local JSON assignment history, role-enforced assignment APIs, queue pages, workload metrics, and SLA risk indicators.

The notification system is documented in [docs/notification-system.md](docs/notification-system.md). It includes local in-app notifications, preferences, templates, delivery history, external channel placeholders, audit, telemetry, and frontend inbox pages.

Local verification:

1. Start the backend and frontend with `start-local.bat`.
2. Open `http://localhost:3000/login` and select a demo role.
3. Open `http://localhost:3000/cases/case-001`.
4. Submit a human review as `FRAUD_ANALYST` with `HOLD`.
5. Confirm the audit trail records the authenticated actor and status change.
6. Submit `ESCALATE` on `case-001` with an override reason to verify the override banner and `HUMAN_OVERRIDE_DETECTED` audit event.
7. Open `http://localhost:3000/metrics` to review AI-human agreement, override rate, operational, RAG, agent, and audit metrics.
8. Log in as `ADMIN`, open `http://localhost:3000/alerts`, simulate an alert, then open `http://localhost:3000/incidents` to review the generated incident.
9. Open `http://localhost:3000/cost` to review token usage, estimated cost, budgets, and anomaly indicators.
10. Open `http://localhost:3000/admin/config` as `ADMIN` to inspect safe configuration, update `RAG_TOP_K`, and review config history.
11. Open `http://localhost:3000/queues/my` as `FRAUD_ANALYST` or `http://localhost:3000/queues/team` as `FRAUD_MANAGER` to verify assignment queues.
12. Open `http://localhost:3000/admin/notifications` as `ADMIN`, send a test notification, then review it at `http://localhost:3000/notifications`.

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
- Fraud case dashboard APIs
- Local deterministic agent investigation workflow
- Local and Azure-ready RAG structure
- Human review workflow with role permissions
- Audit trail persistence
- Evaluation metrics dashboard
- Observability telemetry fallback
- Alerting and incident response MVP with runbooks
- Cost monitoring and token usage dashboard with local estimates
- Admin Configuration Panel with safe non-secret runtime overrides and feature flags
- Case assignment, investigator queues, workload summary, assignment history, and SLA risk tracking
- Notification system with in-app inbox, local delivery history, templates, preferences, audit, and telemetry

Still placeholder-only:

- Production Azure Monitor alert deployment
- Production Teams, email, and ticketing integrations
- Real database persistence
# AI Feedback Loop

Investigators can submit structured feedback on AI summaries, recommendations, policy citations, similar cases, risk indicators, reviewer validation, and agent traces from the case detail page after running an AI investigation. Feedback is stored locally in `data/synthetic/ai_feedback.json`, critical items create backlog records in `data/synthetic/ai_improvement_backlog.json`, and accepted feedback can be exported as a sanitized evaluation dataset.

# Deployment Hardening

Production deployment is prepared for Key Vault-backed secrets, managed identity, RBAC, public network access controls, and private endpoint scaffolding. Local mode remains available without Azure dependencies. See `docs/deployment-hardening-key-vault-private-endpoints-managed-identity.md`.
