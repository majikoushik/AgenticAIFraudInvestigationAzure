def retrieve_by_keyword(query: str, documents: list[tuple[str, str]]) -> list[tuple[str, str]]:
    normalized_query = query.lower()
    return [
        (name, content)
        for name, content in documents
        if normalized_query in content.lower()
    ]
