from agents.safety.output_validator import OutputValidator


def evaluate_safety(summary: dict) -> dict:
    result = OutputValidator().validate_summary(summary)
    return {"safe": result["passed"], "safety_flags": result["safety_flags"], "validation_errors": result["validation_errors"]}
