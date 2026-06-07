# RAG

Local-first and Azure AI Search-ready retrieval layer for fraud investigation policies, historical cases, SOPs, and synthetic case evidence.

## Local Mode

Local mode is the default and requires no Azure credentials:

```env
USE_AZURE_SEARCH=false
```

The investigation agents use:

- `rag/sample_documents/policies/` for policy keyword retrieval
- `data/synthetic/historical_cases.json` for historical case similarity
- `data/synthetic/*.json` for local case evidence search APIs

## Azure AI Search Mode

Azure mode is enabled only when explicitly configured:

```env
USE_AZURE_SEARCH=true
AZURE_SEARCH_ENDPOINT=https://placeholder.search.windows.net
AZURE_SEARCH_QUERY_KEY=placeholder-only
AZURE_SEARCH_ADMIN_KEY=placeholder-only
AZURE_SEARCH_POLICY_INDEX=fraud-policies
AZURE_SEARCH_HISTORICAL_CASE_INDEX=historical-fraud-cases
AZURE_SEARCH_EVIDENCE_INDEX=case-evidence
AZURE_SEARCH_SEMANTIC_CONFIG=fraud-semantic-config
```

Use secure configuration for real deployments. `.env.example` values are placeholders only.

## Indexes

Create or update indexes:

```bash
python -m rag.indexes.create_indexes
```

Reset indexes:

```bash
python -m rag.indexes.reset_indexes --confirm
```

Delete indexes:

```bash
python -m rag.indexes.delete_indexes --confirm
```

Index schema modules:

- `rag/indexes/policy_index_schema.py`
- `rag/indexes/historical_case_index_schema.py`
- `rag/indexes/case_evidence_index_schema.py`

## Ingestion

Policy documents:

```bash
python -m rag.ingestion.ingest_policy_documents --input rag/documents/policies
```

Historical cases:

```bash
python -m rag.ingestion.ingest_historical_cases --input rag/documents/historical_cases
```

Synthetic case evidence:

```bash
python -m rag.ingestion.ingest_case_evidence --input data/synthetic
```

Embedding generation is disabled by default. Set `USE_AZURE_OPENAI_EMBEDDINGS=true` and configure Azure OpenAI embedding values only when you want vector or hybrid search.

## Backend APIs

- `GET /api/v1/rag/health`
- `POST /api/v1/rag/search/policies`
- `POST /api/v1/rag/search/historical-cases`
- `POST /api/v1/rag/search/case-evidence`
- `POST /api/v1/rag/search/all`

Responses include citation metadata, scores, source filenames, chunk ids when available, and retrieval mode.

## Evaluation

Run the local retrieval smoke evaluation:

```bash
python -m rag.evaluation.run_local_eval
```

The dataset lives in `rag/evaluation/evaluation_dataset.json`.
