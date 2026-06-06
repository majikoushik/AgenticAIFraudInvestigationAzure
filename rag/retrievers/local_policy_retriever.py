from pathlib import Path
import re

from rag.retrievers.base_retriever import RetrievalResult


class LocalPolicyRetriever:
    retrieval_mode = "local"

    def __init__(self, policy_directory: Path | None = None) -> None:
        self.policy_directory = policy_directory or self._default_policy_directory()

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        query_terms = self._tokenize(query)
        results: list[RetrievalResult] = []

        for path in sorted(self.policy_directory.glob("*.md")):
            title, sections = self._load_sections(path)
            for section_title, section_text in sections:
                section_terms = self._tokenize(f"{section_title} {section_text}")
                score = len(query_terms.intersection(section_terms))
                if score > 0:
                    results.append(
                        RetrievalResult(
                            title=title,
                            content=self._shorten(section_text),
                            source_file=path.name,
                            score=float(score),
                            metadata={
                                "document_type": "policy",
                                "policy_name": title,
                                "section_title": section_title,
                                "retrieval_mode": self.retrieval_mode,
                            },
                        )
                    )

        return sorted(results, key=lambda result: result.score, reverse=True)[:top_k]

    def _load_sections(self, path: Path) -> tuple[str, list[tuple[str, str]]]:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()
        title = self._clean_heading(lines[0]) if lines else path.stem
        sections: list[tuple[str, str]] = []
        current_title = title
        current_lines: list[str] = []

        for line in lines[1:]:
            if line.startswith("## "):
                if current_lines:
                    sections.append((current_title, " ".join(current_lines).strip()))
                current_title = self._clean_heading(line)
                current_lines = []
            elif line.strip():
                current_lines.append(line.strip())

        if current_lines:
            sections.append((current_title, " ".join(current_lines).strip()))

        return title, sections

    @staticmethod
    def _default_policy_directory() -> Path:
        return Path(__file__).resolve().parents[1] / "sample_documents" / "policies"

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9_]+", text.lower()) if len(token) > 2}

    @staticmethod
    def _clean_heading(line: str) -> str:
        return line.lstrip("#").strip()

    @staticmethod
    def _shorten(text: str, limit: int = 260) -> str:
        return text if len(text) <= limit else f"{text[:limit].rstrip()}..."
