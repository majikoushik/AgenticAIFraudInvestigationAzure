# 3. Modular Deterministic Agents Before Live LLMs

Date: 2026-06-23

## Status
Accepted

## Context
Running real LLMs during local development incurs costs, latency, and requires secure credential management. It also makes tests non-deterministic.

## Decision
We implemented the Agent orchestration using deterministic, mock agent classes for the MVP. They simulate the exact input/output contracts that the target Azure OpenAI or Azure AI Foundry Agent Service would use.

## Consequences
- **Positive:** Tests and local development are fast, free, and deterministic. The architecture proves the boundaries of the Agent layer.
- **Negative:** We do not get real LLM feedback loops locally by default, potentially hiding prompt engineering issues until testing in the cloud.
