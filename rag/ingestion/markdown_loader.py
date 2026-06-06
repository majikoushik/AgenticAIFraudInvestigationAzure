from pathlib import Path


def load_markdown_documents(directory: str) -> list[tuple[str, str]]:
    documents: list[tuple[str, str]] = []
    for path in Path(directory).glob("*.md"):
        documents.append((path.name, path.read_text(encoding="utf-8")))
    return documents
