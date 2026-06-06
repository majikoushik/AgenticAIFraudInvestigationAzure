import json
from pathlib import Path
from typing import Any

from app.config import get_synthetic_data_path


class JsonRepository:
    def __init__(self, data_path: Path | None = None) -> None:
        self.data_path = data_path or get_synthetic_data_path()

    def read_list(self, file_name: str) -> list[dict[str, Any]]:
        file_path = self.data_path / file_name
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(f"Expected {file_name} to contain a JSON array.")

        return data
