"""
Pydantic schemas for the Production Readiness Framework.
All models use strict typing and exclude secrets.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Check Definition
# ---------------------------------------------------------------------------

class ReadinessCheckDefinition(BaseModel):
    """Static definition of a readiness check (from the registry)."""

    check_id: str
    category: str
    title: str
    description: str
    check_type: str  # AUTOMATED | MANUAL | HYBRID
    severity: str    # BLOCKER | HIGH | MEDIUM | LOW | INFO
    automated: bool
    manual_evidence_required: bool
    recommended_evidence: str
    remediation: str
    owner: str


# ---------------------------------------------------------------------------
# Check Result
# ---------------------------------------------------------------------------

class ReadinessCheckResult(BaseModel):
    """Result of executing a single readiness check."""

    check_id: str
    category: str
    title: str
    status: str       # ReadinessStatus value
    severity: str     # ReadinessSeverity value
    score: float      # 0–100
    message: str
    evidence: list[str] = Field(default_factory=list)
    automated_result: dict[str, Any] = Field(default_factory=dict)
    manual_notes: str | None = None
    remediation: str
    checked_at: str   # UTC ISO timestamp


# ---------------------------------------------------------------------------
# Category Result
# ---------------------------------------------------------------------------

class ReadinessCategoryResult(BaseModel):
    """Aggregated result for a single readiness category."""

    category: str
    score: float
    pass_count: int
    fail_count: int
    warning_count: int
    manual_review_count: int
    not_checked_count: int
    not_applicable_count: int
    blocker_fail_count: int
    checks: list[ReadinessCheckResult]


# ---------------------------------------------------------------------------
# Assessment Request / Response
# ---------------------------------------------------------------------------

class ReadinessAssessmentRequest(BaseModel):
    environment: str = "prod"
    categories: list[str] | None = None  # None = all categories
    create_risks_from_failures: bool = True
    comment: str | None = None


class ReadinessAssessmentResponse(BaseModel):
    assessment_id: str
    environment: str
    overall_score: float
    go_live_decision: str
    blocking_issue_count: int
    high_risk_count: int
    warning_count: int
    manual_review_required_count: int
    category_results: list[ReadinessCategoryResult]
    top_risks: list[str]
    created_by: str
    created_at: str
    summary: str


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------

class ReadinessEvidenceUpdateRequest(BaseModel):
    check_id: str
    evidence_type: str = "TEXT"   # TEXT | FILE_REFERENCE | URL | CHECK_OUTPUT
    description: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReadinessEvidenceItem(BaseModel):
    evidence_id: str
    check_id: str
    assessment_id: str
    evidence_type: str
    description: str
    submitted_by: str
    submitted_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Risk Register
# ---------------------------------------------------------------------------

class ReadinessRiskItem(BaseModel):
    risk_id: str
    title: str
    description: str
    category: str
    severity: str
    status: str   # OPEN | MITIGATED | ACCEPTED | CLOSED
    owner: str
    mitigation_plan: str | None = None
    target_date: str | None = None
    created_at: str
    updated_at: str
    created_by: str | None = None
    assessment_id: str | None = None
    check_id: str | None = None
    close_comment: str | None = None


class ReadinessRiskCreateRequest(BaseModel):
    title: str
    description: str
    category: str
    severity: str
    owner: str
    mitigation_plan: str | None = None
    target_date: str | None = None


class ReadinessRiskUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    owner: str | None = None
    mitigation_plan: str | None = None
    target_date: str | None = None


class ReadinessRiskCloseRequest(BaseModel):
    comment: str | None = None


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

class ReadinessReportResponse(BaseModel):
    assessment_id: str
    format: str
    export_path: str
    content_preview: str  # First 500 chars of the report
    exported_at: str


# ---------------------------------------------------------------------------
# Go-live Decision
# ---------------------------------------------------------------------------

class GoLiveDecisionResponse(BaseModel):
    assessment_id: str
    environment: str
    go_live_decision: str
    overall_score: float
    blocking_issue_count: int
    high_risk_count: int
    warning_count: int
    manual_review_required_count: int
    rationale: str
    created_at: str
