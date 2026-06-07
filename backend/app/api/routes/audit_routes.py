from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.repositories.case_repository import CaseRepository
from app.core.constants import AUDIT_EVENT_CATEGORY_BY_TYPE, AuditEventType
from app.schemas.audit_schema import AuditEventListResponse
from app.services.audit_service import audit_service
from app.services.case_service import CaseService
from app.services.case_status_service import case_status_service

router = APIRouter(prefix="/cases", tags=["audit"])
case_service = CaseService(CaseRepository(), audit_service, case_status_service)


@router.get("/{case_id}/audit", response_model=AuditEventListResponse)
def get_case_audit(case_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_AUDIT))) -> AuditEventListResponse:
    del current_user
    case_service.ensure_case_exists(case_id)
    return audit_service.get_case_audit_trail(case_id)


audit_router = APIRouter(prefix="/audit", tags=["audit"])


@audit_router.get("/search", response_model=AuditEventListResponse)
def search_audit_events(
    case_id: str | None = None,
    event_type: str | None = None,
    actor: str | None = None,
    actor_role: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_AUDIT)),
) -> AuditEventListResponse:
    del current_user
    return audit_service.search_audit_events(case_id, event_type, actor, actor_role, start_date, end_date)


@audit_router.get("/event-types")
def get_audit_event_types(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_AUDIT))) -> dict:
    del current_user
    return {
        "event_types": [
            {
                "event_type": event_type.value,
                "event_category": AUDIT_EVENT_CATEGORY_BY_TYPE[event_type],
            }
            for event_type in AuditEventType
        ]
    }


@audit_router.get("/summary")
def get_audit_summary(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_AUDIT))) -> dict:
    del current_user
    events = audit_service.search_audit_events().events
    by_category: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for event in events:
        by_category[event.event_category] = by_category.get(event.event_category, 0) + 1
        by_type[event.event_type.value] = by_type.get(event.event_type.value, 0) + 1
    return {"count": len(events), "by_category": by_category, "by_type": by_type}
