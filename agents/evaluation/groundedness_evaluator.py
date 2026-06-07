from agents.safety.citation_validator import CitationValidator


def evaluate_groundedness(output_references: list[dict], retrieved_references: list[dict]) -> dict:
    result = CitationValidator().validate(output_references, retrieved_references)
    return {"grounded": result["passed"], "citation_issues": result["citation_issues"]}
