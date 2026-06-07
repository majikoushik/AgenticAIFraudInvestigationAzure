import json
from pathlib import Path
from typing import Any


def resolve_store_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return Path(__file__).resolve().parents[3] / path


class JsonFileStore:
    def __init__(self, path_text: str) -> None:
        self.path = resolve_store_path(path_text)

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            self.write([])
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8") or "[]")
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    def write(self, records: list[dict[str, Any]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temp.write_text(json.dumps(records, indent=2, default=str), encoding="utf-8")
        temp.replace(self.path)
