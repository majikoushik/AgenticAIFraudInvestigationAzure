# 2. FastAPI Backend Boundary

Date: 2026-06-23

## Status
Accepted

## Context
We need a robust, performant, and secure API layer to broker communication between the React frontend, the AI agents, and our data stores.

## Decision
We selected FastAPI for the backend service. It natively supports Python (the primary language for AI SDKs), offers out-of-the-box OpenAPI documentation, and uses Pydantic for strong request/response validation.

## Consequences
- **Positive:** Seamless integration with Pydantic ensures strong type safety and explicit API contracts.
- **Negative:** We must be careful to avoid blocking the async event loop when calling synchronous AI SDK methods.
