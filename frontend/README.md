# Frontend

Next.js TypeScript dashboard for the Agentic AI Fraud Investigation MVP.

## Features

- Enterprise-style dashboard with case statistics and recent alerts.
- Fraud case queue with risk badges and case navigation.
- Case detail workspace with customer, transaction, beneficiary, device, risk indicator, AI investigation, reviewer validation, decision, and audit panels.
- Human review workflow with role-based decision form, evidence acknowledgement, policy acknowledgement, override reason handling, and audit timeline.
- Runtime integration with the FastAPI backend.
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

## Environment Variables

Create `.env.local` from `.env.example` when overriding defaults.

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Agentic AI Fraud Investigation
```

## Validation

```bash
npm run lint
npm run build
```
