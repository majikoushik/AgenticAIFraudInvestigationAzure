import argparse
import json

from rag.indexes.create_indexes import create_indexes
from rag.indexes.delete_indexes import delete_indexes


def reset_indexes(confirm: bool = False) -> dict:
    if not confirm:
        return {"warning": "Pass --confirm to delete and recreate indexes."}
    return {"delete": delete_indexes(True), "create": create_indexes()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true")
    print(json.dumps(reset_indexes(parser.parse_args().confirm), indent=2))
