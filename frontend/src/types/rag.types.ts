export type RagCitation = {
  source?: string;
  title?: string;
  section?: string;
  chunk_id?: string;
};

export type RagRetrievalResult = {
  title: string;
  source_filename: string;
  source_path?: string;
  matched_section: string;
  snippet: string;
  score: number;
  reranker_score: number;
  retrieval_mode: string;
  citation: RagCitation;
  chunk_id?: string;
  metadata: Record<string, unknown>;
  explanation?: string;
};

export type RagSearchResponse = {
  query: string;
  retrieval_mode: string;
  index_type: string;
  results: RagRetrievalResult[];
};

export type RagSearchAllResponse = {
  query: string;
  retrieval_mode: string;
  policies: RagRetrievalResult[];
  historical_cases: RagRetrievalResult[];
  case_evidence: RagRetrievalResult[];
};
