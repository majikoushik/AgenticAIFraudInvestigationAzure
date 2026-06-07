from rag.retrievers.base_retriever import RetrievalResult


def build_citation(result: RetrievalResult) -> dict:
    citation = result.citation or {
        "source": result.source_file,
        "title": result.title,
        "section": result.metadata.get("section_title", result.title),
        "chunk_id": result.metadata.get("chunk_id") or result.id,
    }
    return {
        "title": result.title,
        "source_filename": result.source_file,
        "source_path": result.source_path,
        "matched_section": result.metadata.get("section_title", result.title),
        "snippet": result.content,
        "score": result.score,
        "reranker_score": result.reranker_score,
        "retrieval_mode": result.metadata.get("retrieval_mode", "local"),
        "citation": citation,
        "chunk_id": citation.get("chunk_id"),
        "metadata": result.metadata,
    }


def build_policy_reference(result: RetrievalResult) -> dict:
    citation = build_citation(result)
    return {
        **citation,
        "explanation": result.metadata.get(
            "explanation",
            "Matched policy retrieval result from the configured RAG retriever.",
        ),
    }
