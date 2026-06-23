# 4. Local/Azure-Ready RAG Abstraction

Date: 2026-06-23

## Status
Accepted

## Context
Retrieval-Augmented Generation (RAG) is essential for grounding agent decisions in banking policies. Setting up Azure AI Search locally is complex and not cost-effective for a simple MVP.

## Decision
We abstract the retrieval layer. In local mode, we use a simple keyword-based search over local Markdown documents. The abstraction boundary ensures that switching to Azure AI Search is just a matter of changing the implementation class and configuring environment variables.

## Consequences
- **Positive:** Fast local development without cloud dependencies. Clean architecture boundaries.
- **Negative:** Keyword search lacks the semantic understanding of vector search, which might lead to lower relevance in local testing.
