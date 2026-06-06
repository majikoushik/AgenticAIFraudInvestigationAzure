from fastapi import APIRouter, Query

from app.schemas.rag_schema import PolicySearchResponse
from app.services.rag_service import RagService

router = APIRouter(prefix="/rag", tags=["rag"])
rag_service = RagService()


@router.get("/policies/search", response_model=PolicySearchResponse)
def search_policies(query: str = Query(..., min_length=1), top_k: int = Query(3, ge=1, le=10)) -> PolicySearchResponse:
    return rag_service.search_policies(query=query, top_k=top_k)
