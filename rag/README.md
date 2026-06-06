# RAG

Local and Azure AI Search-ready retrieval layer for fraud investigation policies and historical cases.

## Local Retrieval

Local mode requires no Azure credentials. Policy markdown documents are loaded from:

```text
rag/sample_documents/policies/
```

The local retriever performs keyword matching over markdown section text and returns policy references with source filenames and matched sections.

Set:

```env
USE_AZURE_SEARCH=false
```

## Azure AI Search Retrieval

Azure mode uses Azure AI Search indexes for policy and historical case retrieval. If Azure Search is enabled but required settings are missing, the hybrid policy retriever falls back to local mode.

Required environment variables:

```env
AZURE_SEARCH_ENDPOINT=
AZURE_SEARCH_ADMIN_KEY=
AZURE_SEARCH_POLICY_INDEX=fraud-policies
AZURE_SEARCH_CASE_INDEX=historical-fraud-cases
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
USE_AZURE_SEARCH=false
```

`AZURE_OPENAI_*` variables are only required when generating embeddings. Without them, ingestion uploads empty vectors and prints a warning.

## Create Indexes

```bash
python -m rag.indexes.create_indexes
```

The script creates or updates:

- `fraud-policies`
- `historical-fraud-cases`

Index schemas are stored under `rag/indexes/`.

## Ingest Policy Documents

```bash
python -m rag.ingestion.ingest_policy_documents
```

This loads markdown policies, chunks them, optionally generates embeddings, and uploads documents to the policy index.

## Ingest Historical Cases

```bash
python -m rag.ingestion.ingest_historical_cases
```

This loads `data/synthetic/historical_cases.json`, converts cases into searchable documents, optionally generates embeddings, and uploads them to the historical case index.

## Agents

`PolicyRagAgent` uses `HybridPolicyRetriever`:

- Azure AI Search when `USE_AZURE_SEARCH=true` and Azure Search config is present
- Local keyword retrieval otherwise

`HistoricalCaseAgent` uses Azure AI Search for historical cases when configured, with local JSON similarity fallback.

Both modes return the same response shape to the backend orchestration layer.
