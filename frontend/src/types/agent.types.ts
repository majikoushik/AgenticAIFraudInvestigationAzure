import type { RiskIndicator } from "@/types/case.types";

export type AgentTraceItem = {
  agent: string;
  output: Record<string, unknown>;
};

export type PolicyReference = {
  title: string;
  source_filename: string;
  source_path?: string;
  matched_section: string;
  snippet: string;
  explanation: string;
  score?: number;
  reranker_score?: number;
  retrieval_mode?: string;
  chunk_id?: string;
  citation?: {
    source?: string;
    title?: string;
    section?: string;
    chunk_id?: string;
  };
  metadata?: Record<string, unknown>;
};

export type SimilarCase = {
  case_id: string;
  outcome: string;
  summary: string;
  matched_risk_indicators: string[];
  similarity_score: number;
  source_filename?: string;
  citation?: PolicyReference;
};

export type InvestigationSummary = {
  case_overview: string;
  key_risk_indicators: RiskIndicator[];
  evidence_supporting_suspicion: string[];
  evidence_reducing_suspicion: string[];
  policy_references: PolicyReference[];
  similar_cases: SimilarCase[];
  recommended_action: string;
  confidence_level: string;
  missing_evidence: string[];
  human_review_requirement: string;
  grounding?: {
    policy_retrieval_mode: string;
    policy_source_count: number;
    policy_citation_count: number;
    historical_case_retrieval_mode: string;
    historical_case_source_count: number;
  };
};

export type ReviewerValidation = {
  is_evidence_supported: boolean;
  unsupported_claims: string[];
  human_review_required: boolean;
  review_notes: string[];
};

export type InvestigationPackage = {
  case_id: string;
  agent_trace: AgentTraceItem[];
  risk_indicators: RiskIndicator[];
  policy_references: PolicyReference[];
  similar_cases: SimilarCase[];
  investigation_summary: InvestigationSummary;
  reviewer_validation: ReviewerValidation;
  human_review_required: boolean;
};
