from typing import Any

from pydantic import BaseModel


class PolicySearchResponse(BaseModel):
    query: str
    retrieval_mode: str
    results: list[dict[str, Any]]
