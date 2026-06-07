import argparse
import json
from pathlib import Path

from rag.config.rag_config import rag_config
from rag.ingestion.ingestion_pipeline import IngestionPipeline


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(Path(__file__).resolve().parents[1] / "documents" / "policies"))
    parser.add_argument("--index", default=rag_config.policy_index)
    args = parser.parse_args()
    print(json.dumps(IngestionPipeline().run(args.input, "POLICY", args.index), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
