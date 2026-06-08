# Frontend

Next.js TypeScript dashboard for the Agentic AI Fraud Investigation MVP.

## Features

- Enterprise-style dashboard with case statistics and recent alerts.
- Fraud case queue with risk badges and case navigation.
- Case detail workspace with customer, transaction, beneficiary, device, risk indicator, AI investigation, reviewer validation, decision, and audit panels.
- Human review workflow with role-based decision form, evidence acknowledgement, policy acknowledgement, override reason handling, and audit timeline.
- Evaluation metrics dashboard at `/metrics` for AI-human agreement, override rate, operational timing, agent, RAG, policy, and audit metrics.
- Local demo authentication and Entra ID-ready auth structure.
- Runtime integration with the FastAPI backend.
- AI provider badge, token usage, latency, safety flags, citation issues, and reviewer validation display.
- Observability page at `/observability` for admin users, showing backend health details, telemetry configuration, and recent local telemetry events.
- Admin alerting page at `/alerts` for listing and simulating local alerts.
- Admin incident pages at `/incidents` and `/incidents/[incidentId]` for triage, status updates, assignment, timeline notes, and closure.
- Cost monitoring dashboard at `/cost` for token usage, estimated cost, agent/model cost, budgets, and anomaly indicators.
- Admin Configuration Panel at `/admin/config` for safe non-secret runtime settings, feature flags, health, history, and reset controls.
- Local-only MVP behavior with no direct external AI calls.

## Install

```bash
npm install
```

## Run Locally

Start the backend first:

```bash
cd ../backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then start the frontend:

```bash
npm run dev
```

The app runs at `http://localhost:3000`.

Open `http://localhost:3000/metrics` to view the evaluation dashboard.
Open `http://localhost:3000/alerts` as an admin to simulate and inspect alert events.
Open `http://localhost:3000/incidents` as an admin to manage generated incidents.
Open `http://localhost:3000/cost` to review estimated cost and token usage.
Open `http://localhost:3000/admin/config` as `ADMIN` to manage safe configuration overrides.
Open `http://localhost:3000/login` to select a local demo role when `NEXT_PUBLIC_AUTH_MODE=local`.

## Environment Variables

Create `.env.local` from `.env.example` when overriding defaults.

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Agentic AI Fraud Investigation
NEXT_PUBLIC_AUTH_MODE=local
NEXT_PUBLIC_ENTRA_CLIENT_ID=
NEXT_PUBLIC_ENTRA_TENANT_ID=
NEXT_PUBLIC_ENTRA_AUTHORITY=
NEXT_PUBLIC_ENTRA_REDIRECT_URI=http://localhost:3000
NEXT_PUBLIC_API_SCOPE=
```

## Validation

```bash
npm run lint
npm run build
```
