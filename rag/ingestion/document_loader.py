import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LoadedDocument:
    source_file: str
    title: str
    document_type: str
    content: str
    created_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentLoader:
    def load_markdown_directory(self, directory: str | Path) -> list[LoadedDocument]:
        return [self.load_markdown_file(path) for path in sorted(Path(directory).glob("*.md"))]

    def load_markdown_file(self, path: str | Path) -> LoadedDocument:
        file_path = Path(path)
        content = file_path.read_text(encoding="utf-8")
        title = self._first_markdown_heading(content) or file_path.stem.replace("-", " ").title()
        return LoadedDocument(
            source_file=file_path.name,
            title=title,
            document_type="policy",
            content=content,
            created_at=datetime.fromtimestamp(file_path.stat().st_mtime, UTC).isoformat(),
            metadata={"policy_name": title, "source_path": str(file_path)},
        )

    def load_historical_cases(self, path: str | Path) -> list[LoadedDocument]:
        file_path = Path(path)
        cases = json.loads(file_path.read_text(encoding="utf-8"))
        documents: list[LoadedDocument] = []

        for case in cases:
            title = f"Historical fraud case {case['case_id']}"
            content = " ".join(
                [
                    title,
                    case.get("summary", ""),
                    f"Outcome: {case.get('outcome', 'unknown')}",
                    f"Risk indicators: {', '.join(case.get('risk_indicators', []))}",
                ]
            )
            documents.append(
                LoadedDocument(
                    source_file=file_path.name,
                    title=title,
                    document_type="historical_case",
                    content=content,
                    created_at=case.get("created_at"),
                    metadata={
                        "case_id": case["case_id"],
                        "case_type": case.get("case_type", "historical_fraud_case"),
                        "risk_indicators": case.get("risk_indicators", []),
                        "outcome": case.get("outcome", "unknown"),
                    },
                )
            )

        return documents

    @staticmethod
    def _first_markdown_heading(content: str) -> str | None:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.lstrip("#").strip()
        return None
