from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.compliance.compliance_export_service import compliance_export_service
from app.compliance.compliance_report_service import compliance_report_service
from app.schemas.compliance_schema import ComplianceExportCreateRequest

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.get("/summary")
def get_compliance_summary(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> dict:
    return compliance_report_service.get_compliance_summary()


@router.get("/retention-summary")
def get_retention_summary(current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> dict:
    return compliance_report_service.get_retention_summary()


@router.post("/exports/case/{case_id}")
def create_case_export(case_id: str, request: ComplianceExportCreateRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.CREATE_COMPLIANCE_EXPORT))) -> dict:
    return compliance_export_service.create_case_compliance_export(case_id, current_user.user_id, request.model_dump())


@router.get("/exports/{export_id}")
def get_export(export_id: str, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> dict:
    return compliance_export_service.get_export_status(export_id)


@router.get("/exports")
def list_exports(case_id: str | None = None, current_user: AuthenticatedUser = Depends(require_permission(Permission.VIEW_COMPLIANCE))) -> list[dict]:
    return compliance_export_service.list_exports(case_id)
