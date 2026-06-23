"""
Readiness API Routes.
Provides endpoints for running assessments, viewing results, managing risks, and exporting reports.

Security:
  - RUN_READINESS_ASSESSMENT: ADMIN only
  - MANAGE_READINESS_RISKS: ADMIN, COMPLIANCE_OFFICER
  - ADD_READINESS_EVIDENCE: ADMIN, COMPLIANCE_OFFICER
  - EXPORT_READINESS_REPORT: ADMIN, COMPLIANCE_OFFICER, AUDITOR
  - VIEW_READINESS: all roles with explicit grant
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.auth.permissions import Permission, require_permission, assert_permission
from app.dependencies import get_current_user
from app.auth.current_user import AuthenticatedUser
from app.readiness.readiness_config import readiness_config
from app.readiness.readiness_registry import get_all_checks, get_all_categories
from app.readiness.readiness_risk_service import readiness_risk_service
from app.readiness.readiness_service import readiness_service
from app.readiness.readiness_evidence_service import readiness_evidence_service
from app.schemas.readiness_schema import (
    ReadinessAssessmentRequest,
    ReadinessEvidenceUpdateRequest,
    ReadinessRiskCreateRequest,
    ReadinessRiskUpdateRequest,
    ReadinessRiskCloseRequest,
)
from app.services.errors import ApiError

router = APIRouter(prefix="/readiness", tags=["Production Readiness"])


# ---------------------------------------------------------------------------
# 1. Config health
# ---------------------------------------------------------------------------

@router.get("/config/health", summary="Readiness config health")
def get_readiness_config_health(
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Return safe readiness configuration summary — no secrets."""
    assert_permission(current_user, Permission.VIEW_READINESS)
    return {
        "status": "ok",
        "config": readiness_config.safe_summary(),
    }


# ---------------------------------------------------------------------------
# 2. Checklist definitions
# ---------------------------------------------------------------------------

@router.get("/checklist", summary="Get readiness checklist definitions")
def get_checklist(
    category: str | None = Query(None, description="Filter by category"),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    """Return all check definitions, optionally filtered by category."""
    assert_permission(current_user, Permission.VIEW_READINESS)
    checks = get_all_checks()
    if category:
        checks = [c for c in checks if c["category"] == category]
    # Group by category
    grouped: dict[str, list] = {}
    for c in checks:
        grouped.setdefault(c["category"], []).append(c)
    return {
        "total": len(checks),
        "categories": get_all_categories(),
        "checklist": grouped,
    }


# ---------------------------------------------------------------------------
# 3. Run assessment
# ---------------------------------------------------------------------------

@router.post("/assessments/run", summary="Run production readiness assessment")
def run_assessment(
    payload: ReadinessAssessmentRequest,
    current_user: AuthenticatedUser = Depends(
        require_permission(Permission.RUN_READINESS_ASSESSMENT)
    ),
) -> dict[str, Any]:
    """Execute a full readiness assessment. Requires ADMIN role."""
    assessment = readiness_service.run_assessment(
        environment=payload.environment,
        categories=payload.categories,
        create_risks=payload.create_risks_from_failures,
        comment=payload.comment,
        requested_by=current_user.user_id,
    )
    return assessment


# ---------------------------------------------------------------------------
# 4. List assessments
# ---------------------------------------------------------------------------

@router.get("/assessments", summary="List readiness assessments")
def list_assessments(
    environment: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.VIEW_READINESS)
    items = readiness_service.list_assessments(environment=environment, limit=limit)
    return {"count": len(items), "assessments": items}


# ---------------------------------------------------------------------------
# 5. Get assessment by ID
# ---------------------------------------------------------------------------

@router.get("/assessments/{assessment_id}", summary="Get assessment by ID")
def get_assessment(
    assessment_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.VIEW_READINESS)
    assessment = readiness_service.get_assessment(assessment_id)
    if not assessment:
        raise ApiError(404, "not_found", f"Assessment {assessment_id} not found.")
    return assessment


# ---------------------------------------------------------------------------
# 6. Get category result
# ---------------------------------------------------------------------------

@router.get("/assessments/{assessment_id}/category/{category}", summary="Get category result")
def get_category_result(
    assessment_id: str,
    category: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.VIEW_READINESS)
    result = readiness_service.get_category_result(assessment_id, category)
    if not result:
        raise ApiError(404, "not_found", f"Category {category} not found in assessment {assessment_id}.")
    return result


# ---------------------------------------------------------------------------
# 7. Go-live decision
# ---------------------------------------------------------------------------

@router.get("/assessments/{assessment_id}/go-live-decision", summary="Get go-live decision")
def get_go_live_decision(
    assessment_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.VIEW_READINESS)
    decision = readiness_service.get_go_live_decision(assessment_id)
    if not decision:
        raise ApiError(404, "not_found", f"Assessment {assessment_id} not found.")
    return decision


# ---------------------------------------------------------------------------
# 8. Add evidence
# ---------------------------------------------------------------------------

@router.post("/assessments/{assessment_id}/evidence", summary="Add evidence to check")
def add_evidence(
    assessment_id: str,
    payload: ReadinessEvidenceUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.ADD_READINESS_EVIDENCE)
    evidence = readiness_evidence_service.add_evidence(
        assessment_id=assessment_id,
        check_id=payload.check_id,
        evidence_type=payload.evidence_type,
        description=payload.description,
        submitted_by=current_user.user_id,
        metadata=payload.metadata,
    )
    if not evidence:
        raise ApiError(404, "not_found", f"Assessment {assessment_id} not found.")
    return evidence


# ---------------------------------------------------------------------------
# 9. Export report
# ---------------------------------------------------------------------------

@router.post("/assessments/{assessment_id}/export", summary="Export readiness report")
def export_report(
    assessment_id: str,
    format: str = Query("markdown", pattern="^(markdown|json)$"),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.EXPORT_READINESS_REPORT)
    result = readiness_service.export_assessment_report(assessment_id, format)
    if "error" in result:
        raise ApiError(404, "not_found", result["error"])
    return result


# ---------------------------------------------------------------------------
# 10–13. Risk Register
# ---------------------------------------------------------------------------

@router.get("/risks", summary="List risks in the risk register")
def list_risks(
    status: str | None = Query(None),
    category: str | None = Query(None),
    severity: str | None = Query(None),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.VIEW_READINESS)
    risks = readiness_risk_service.list_risks(status=status, category=category, severity=severity)
    return {"count": len(risks), "risks": risks}


@router.post("/risks", summary="Create a risk item")
def create_risk(
    payload: ReadinessRiskCreateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.MANAGE_READINESS_RISKS)
    risk = readiness_risk_service.create_risk(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        severity=payload.severity,
        owner=payload.owner,
        mitigation_plan=payload.mitigation_plan,
        target_date=payload.target_date,
        created_by=current_user.user_id,
    )
    return risk


@router.patch("/risks/{risk_id}", summary="Update a risk item")
def update_risk(
    risk_id: str,
    payload: ReadinessRiskUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.MANAGE_READINESS_RISKS)
    updates = payload.model_dump(exclude_none=True)
    risk = readiness_risk_service.update_risk(risk_id, updates, current_user.user_id)
    if not risk:
        raise ApiError(404, "not_found", f"Risk {risk_id} not found.")
    return risk


@router.post("/risks/{risk_id}/close", summary="Close a risk item")
def close_risk(
    risk_id: str,
    payload: ReadinessRiskCloseRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> dict[str, Any]:
    assert_permission(current_user, Permission.MANAGE_READINESS_RISKS)
    risk = readiness_risk_service.close_risk(risk_id, current_user.user_id, payload.comment)
    if not risk:
        raise ApiError(404, "not_found", f"Risk {risk_id} not found.")
    return risk
