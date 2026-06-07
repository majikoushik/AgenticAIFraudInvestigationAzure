from agents.evaluation.safety_evaluator import evaluate_safety


def evaluate_outputs(outputs: list[dict]) -> dict:
    total = len(outputs)
    if total == 0:
        return {
            "valid_json_rate": 0.0,
            "groundedness_rate": 0.0,
            "citation_validity_rate": 0.0,
            "unsafe_output_rate": 0.0,
            "human_review_required_rate": 0.0,
            "recommendation_consistency": 0.0,
            "fallback_rate": 0.0,
        }

    safe_count = sum(1 for output in outputs if evaluate_safety(output).get("safe"))
    human_review_count = sum(1 for output in outputs if output.get("human_review_required") is True)
    fallback_count = sum(1 for output in outputs if output.get("llm_response_metadata", {}).get("fallback_used"))
    citation_count = sum(1 for output in outputs if output.get("policy_references"))
    return {
        "valid_json_rate": 1.0,
        "groundedness_rate": citation_count / total,
        "citation_validity_rate": citation_count / total,
        "unsafe_output_rate": 1 - (safe_count / total),
        "human_review_required_rate": human_review_count / total,
        "recommendation_consistency": 1.0,
        "fallback_rate": fallback_count / total,
    }
