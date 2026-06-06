from rag.retrievers.base_retriever import RetrievalResult


def build_citation(result: RetrievalResult) -> dict:
    return {
        "title": result.title,
        "source_filename": result.source_file,
        "matched_section": result.metadata.get("section_title", result.title),
        "snippet": result.content,
        "score": result.score,
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
