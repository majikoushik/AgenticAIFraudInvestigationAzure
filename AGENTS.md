# AGENTS.md

## Project Name

agentic-ai-fraud-investigation-azure

## Project Goal

Build an MVP for a production-style Agentic AI Banking Fraud Investigation System on Azure.

The MVP should demonstrate:
- Fraud case ingestion
- Case dashboard backend APIs
- Local synthetic fraud data
- Agentic investigation workflow
- Local RAG simulation using policy documents
- Human-in-the-loop decision workflow
- Audit trail
- Azure-ready folder structure

## Technology Stack

Frontend:
- Next.js
- TypeScript

Backend:
- Python
- FastAPI
- Pydantic
- Uvicorn
- Pytest

Agent Layer:
- Python
- Modular agent classes
- Local deterministic logic for MVP
- Future-ready for Azure OpenAI, Azure AI Foundry Agent Service, or Semantic Kernel

RAG:
- Local markdown documents for MVP
- Keyword retrieval for MVP
- Future-ready for Azure AI Search

Infrastructure:
- Azure Bicep placeholders
- Azure DevOps pipeline placeholders

## Coding Rules

1. Keep code modular and easy to understand.
2. Do not add real secrets, real credentials, or real customer data.
3. Use synthetic data only.
4. Add comments where business logic may not be obvious.
5. Prefer clear function names over clever abstractions.
6. Use Pydantic schemas for API request and response validation.
7. Use structured error responses.
8. Add tests for all important backend and agent functionality.
9. Keep external API calls disabled for MVP unless explicitly requested.
10. Design interfaces so Azure services can be integrated later.

## Security Rules

1. Never hardcode API keys.
2. Never include real banking data.
3. Mask account numbers where displayed.
4. Keep PII handling functions separate.
5. Human review must be required for high-impact decisions.

## Agentic AI Rules

1. The AI system assists fraud investigators.
2. The AI system must not autonomously freeze accounts.
3. The AI system must not accuse customers of fraud.
4. The AI system must return evidence-supported recommendations only.
5. The reviewer agent must flag unsupported claims.
6. All recommendations must include human review requirement.

## Test Requirements

Before completing a task:
- Run backend tests if backend code changed.
- Run frontend build if frontend code changed.
- Ensure imports are valid.
- Ensure app starts locally.