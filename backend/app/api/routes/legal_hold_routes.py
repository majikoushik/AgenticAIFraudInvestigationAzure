from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.compliance.legal_hold_service import legal_hold_service
from app.schemas.legal_hold_schema import LegalHoldCreateRequest, LegalHoldReleaseRequest

router = APIRouter(prefix="/legal-holds", tags=["legal-holds"])
case_router = APIRouter(prefix="/cases", tags=["legal-holds"])


@router.post("")
def create_legal_hold(request: LegalHoldCreateRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_LEGAL_HOLDS))) -> dict:
    return legal_hold_service.create_legal_hold(request, current_user)


@router.get("")
def list_legal_holds(status: str | None = None, case_id: str | None = None, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> list[dict]:
    return legal_hold_service.list_legal_holds(status, case_id)


@router.get("/{legal_hold_id}")
def get_legal_hold(legal_hold_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> dict:
    return legal_hold_service.get_legal_hold(legal_hold_id)


@router.post("/{legal_hold_id}/release")
def release_legal_hold(legal_hold_id: str, request: LegalHoldReleaseRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_LEGAL_HOLDS))) -> dict:
    return legal_hold_service.release_legal_hold(legal_hold_id, request, current_user)


@case_router.get("/{case_id}/legal-holds")
def get_case_legal_holds(case_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> list[dict]:
    return legal_hold_service.get_holds_for_case(case_id)
