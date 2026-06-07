from typing import Any


class CitationValidator:
    def validate(self, output_references: list[dict[str, Any]], retrieved_references: list[dict[str, Any]]) -> dict[str, Any]:
        allowed = {
            (
                reference.get("source_filename") or reference.get("source") or reference.get("citation", {}).get("source"),
                reference.get("chunk_id") or reference.get("citation", {}).get("chunk_id"),
            )
            for reference in retrieved_references
        }
        issues = []
        for reference in output_references:
            key = (
                reference.get("source_filename") or reference.get("source") or reference.get("citation", {}).get("source"),
                reference.get("chunk_id") or reference.get("citation", {}).get("chunk_id"),
            )
            source_only_allowed = any(item[0] == key[0] for item in allowed)
            if key[0] and not (key in allowed or source_only_allowed):
                issues.append({"source": key[0], "chunk_id": key[1], "issue": "invented_or_unretrieved_citation"})
        return {"passed": len(issues) == 0, "citation_issues": issues}
