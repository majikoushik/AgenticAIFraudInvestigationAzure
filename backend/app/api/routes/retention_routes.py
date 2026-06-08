from fastapi import APIRouter, Depends, Query

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.compliance.archival_service import archival_service
from app.compliance.retention_policy_registry import retention_policy_registry
from app.compliance.retention_service import retention_service
from app.compliance.purge_service import purge_service
from app.core.constants import AuditEventType, ReviewerRole
from app.schemas.retention_schema import RetentionActionRequest, RetentionPolicyUpdateRequest, RetentionScanRequest
from app.services.audit_service import audit_service

router = APIRouter(prefix="/retention", tags=["retention"])


@router.get("/policies")
def list_policies(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> list[dict]:
    audit_service.record_event(None, AuditEventType.RETENTION_POLICY_VIEWED, current_user.user_id, ReviewerRole(current_user.primary_role), metadata={"scope": "all"})
    return retention_service.list_policies()


@router.get("/policies/{data_category}")
def get_policy(data_category: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> dict:
    audit_service.record_event(None, AuditEventType.RETENTION_POLICY_VIEWED, current_user.user_id, ReviewerRole(current_user.primary_role), metadata={"data_category": data_category})
    return retention_service.get_policy(data_category)


@router.patch("/policies/{data_category}")
def update_policy(data_category: str, request: RetentionPolicyUpdateRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_RETENTION))) -> dict:
    policy = retention_policy_registry.update_policy(data_category, request.model_dump(exclude_unset=True), current_user.user_id)
    audit_service.record_event(None, AuditEventType.RETENTION_POLICY_UPDATED, current_user.user_id, ReviewerRole(current_user.primary_role), metadata={"data_category": data_category})
    return policy


@router.post("/scan")
def scan_retention(request: RetentionScanRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_RETENTION))) -> dict:
    return retention_service.scan(request.data_category.value if request.data_category else None, request.dry_run)


@router.get("/scans/{scan_id}")
def get_scan(scan_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> dict:
    return retention_service.get_scan(scan_id)


@router.get("/review-queue")
def get_review_queue(
    data_category: str | None = None,
    recommended_action: str | None = None,
    classification: str | None = None,
    legal_hold_status: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
    current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE)),
) -> dict:
    return retention_service.get_review_queue({"data_category": data_category, "recommended_action": recommended_action, "classification": classification, "legal_hold_status": legal_hold_status, "limit": limit})


@router.post("/archive")
def archive_records(request: RetentionActionRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.MANAGE_RETENTION))) -> dict:
    approved_by = request.approved_by or current_user.user_id
    if request.scan_id:
        return archival_service.archive_candidates(request.scan_id, approved_by, request.dry_run, request.record_ids)
    if request.data_category and request.record_ids:
        return {"action": "ARCHIVE", "dry_run": request.dry_run, "requested_by": approved_by, "results": [archival_service.archive_record(request.data_category.value, record_id, approved_by, request.dry_run) for record_id in request.record_ids]}
    return {"action": "ARCHIVE", "dry_run": request.dry_run, "requested_by": approved_by, "processed_count": 0, "blocked_count": 0, "results": []}


@router.post("/purge")
def purge_records(request: RetentionActionRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.EXECUTE_RETENTION_PURGE))) -> dict:
    approved_by = request.approved_by or current_user.user_id
    if request.scan_id:
        return purge_service.purge_candidates(request.scan_id, approved_by, request.dry_run, request.approval_id, request.record_ids)
    if request.data_category and request.record_ids:
        return {"action": "PURGE", "dry_run": request.dry_run, "requested_by": approved_by, "results": [purge_service.purge_record(request.data_category.value, record_id, approved_by, request.dry_run, request.approval_id) for record_id in request.record_ids]}
    return {"action": "PURGE", "dry_run": request.dry_run, "requested_by": approved_by, "processed_count": 0, "blocked_count": 0, "results": []}
