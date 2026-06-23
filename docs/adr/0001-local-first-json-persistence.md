# 1. Local-First JSON Persistence for MVP

Date: 2026-06-23

## Status
Accepted

## Context
The project needs to demonstrate data flows, audit trails, and human-in-the-loop decision tracking without requiring an immediate, complex, and costly cloud database setup like Cosmos DB for every local developer.

## Decision
We will use a local-first JSON persistence pattern (via `json_repository.py`) to store and retrieve data during the MVP stage. This provides a robust enough interface for the application while avoiding heavy infrastructure dependencies.

## Consequences
- **Positive:** Local development is fast and doesn't require Azure credentials or emulation tools. The repository pattern allows swapping to Cosmos DB easily later.
- **Negative:** JSON files can be overwritten or become corrupted in concurrent local setups. Read-only Docker mounts will break the flow and must be carefully managed.
