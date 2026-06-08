from datetime import datetime

from pydantic import BaseModel

from app.schemas.beneficiary_schema import Beneficiary
from app.schemas.customer_schema import CustomerProfile
from app.schemas.device_schema import Device
from app.schemas.evidence_schema import HistoricalCaseSummary, RiskIndicator
from app.schemas.assignment_schema import AssignmentFields
from app.schemas.transaction_schema import Transaction


class CaseSummary(BaseModel):
    case_id: str
    alert_id: str
    customer_id: str
    severity: str
    status: str
    status_updated_at: datetime | None = None
    status_updated_by: str | None = None
    status_comment: str | None = None
    reason: str
    created_at: str
    assignment: AssignmentFields | None = None


class CaseMetadata(BaseModel):
    case_id: str
    alert_id: str
    severity: str
    reason: str
    created_at: str


class OverrideSummary(BaseModel):
    has_override: bool
    ai_recommendation: str | None = None
    human_decision: str | None = None
    override_reason: str | None = None
    override_detected_at: datetime | None = None
    override_detected_by: str | None = None
    override_comparison_status: str


class CaseDetail(BaseModel):
    metadata: CaseMetadata
    customer: CustomerProfile
    suspicious_transaction: Transaction
    beneficiary: Beneficiary | None
    device: Device | None
    initial_risk_indicators: list[RiskIndicator]
    historical_cases: list[HistoricalCaseSummary]
    current_status: str
    status: str
    status_updated_at: datetime | None = None
    status_updated_by: str | None = None
    status_comment: str | None = None
    ai_recommendation: str | None = None
    investigation_summary: dict | None = None
    human_review: dict | None = None
    override_summary: OverrideSummary | None = None
    audit_events: list[dict] = []
    assignment: AssignmentFields | None = None
