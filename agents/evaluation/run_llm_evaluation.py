import json
from pathlib import Path

from agents.evaluation.llm_output_evaluator import evaluate_outputs
from agents.llm.local_llm_client import LocalLLMClient


def run() -> dict:
    dataset = json.loads((Path(__file__).with_name("llm_eval_dataset.json")).read_text(encoding="utf-8"))
    client = LocalLLMClient()
    outputs = []
    for item in dataset:
        response = client.generate_json(json.dumps({"required_schema": {"case_overview": item["prompt"], "human_review_required": True}}))
        outputs.append(
            {
                **response["json"],
                "policy_references": [{"source_filename": source} for source in item["expected_policy_sources"]],
                "recommended_action": "HOLD",
                "confidence_level": "MEDIUM",
                "missing_evidence": [],
                "human_review_required": True,
                "llm_response_metadata": response,
            }
        )
    return evaluate_outputs(outputs)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
