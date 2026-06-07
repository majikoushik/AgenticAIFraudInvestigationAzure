import json
from pathlib import Path

from rag.retrievers.hybrid_retriever import HybridPolicyRetriever


def run() -> dict:
    dataset_path = Path(__file__).with_name("evaluation_dataset.json")
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    retriever = HybridPolicyRetriever()
    rows = []
    for item in dataset:
        results = retriever.search(item["query"], top_k=5)
        sources = {result.source_file for result in results}
        expected = set(item["expected_sources"])
        rows.append(
            {
                "query": item["query"],
                "expected_sources": sorted(expected),
                "retrieved_sources": sorted(sources),
                "matched_expected_sources": sorted(expected.intersection(sources)),
            }
        )
    return {"retrieval_mode": retriever.retrieval_mode, "rows": rows}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
