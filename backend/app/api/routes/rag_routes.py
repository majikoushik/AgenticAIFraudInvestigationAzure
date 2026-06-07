from fastapi import APIRouter, Depends, Query

from app.auth.permissions import Permission, require_permission
from app.auth.current_user import AuthenticatedUser
from app.schemas.rag_schema import RagHealthResponse, RagSearchAllResponse, RagSearchRequest, RagSearchResponse, PolicySearchResponse
from app.services.rag_service import RagService

router = APIRouter(prefix="/rag", tags=["rag"])
rag_service = RagService()


@router.get("/policies/search", response_model=PolicySearchResponse)
def search_policies(
    query: str = Query(..., min_length=1),
    top_k: int = Query(3, ge=1, le=10),
    _: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASE_DETAILS)),
) -> PolicySearchResponse:
    return rag_service.search_policies(query=query, top_k=top_k)


@router.get("/health", response_model=RagHealthResponse)
def rag_health(_: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASE_DETAILS))) -> RagHealthResponse:
    return rag_service.get_health()


@router.post("/search/policies", response_model=PolicySearchResponse)
def search_policies_post(
    request: RagSearchRequest,
    _: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASE_DETAILS)),
) -> PolicySearchResponse:
    return rag_service.search_policies(query=request.query, top_k=request.top_k, case_id=request.case_id)


@router.post("/search/historical-cases", response_model=RagSearchResponse)
def search_historical_cases(
    request: RagSearchRequest,
    _: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASE_DETAILS)),
) -> RagSearchResponse:
    return rag_service.search_historical_cases(query=request.query, top_k=request.top_k, case_id=request.case_id, filters=request.filters)


@router.post("/search/case-evidence", response_model=RagSearchResponse)
def search_case_evidence(
    request: RagSearchRequest,
    _: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASE_DETAILS)),
) -> RagSearchResponse:
    return rag_service.search_case_evidence(query=request.query, top_k=request.top_k, case_id=request.case_id, filters=request.filters)


@router.post("/search/all", response_model=RagSearchAllResponse)
def search_all(
    request: RagSearchRequest,
    _: AuthenticatedUser = Depends(require_permission(Permission.VIEW_CASE_DETAILS)),
) -> RagSearchAllResponse:
    return rag_service.search_all(query=request.query, top_k=request.top_k, case_id=request.case_id)
