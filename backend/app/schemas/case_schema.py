from pydantic import BaseModel

from app.schemas.beneficiary_schema import Beneficiary
from app.schemas.customer_schema import CustomerProfile
from app.schemas.device_schema import Device
from app.schemas.evidence_schema import HistoricalCaseSummary, RiskIndicator
from app.schemas.transaction_schema import Transaction


class CaseSummary(BaseModel):
    case_id: str
    alert_id: str
    customer_id: str
    severity: str
    status: str
    reason: str
    created_at: str


class CaseMetadata(BaseModel):
    case_id: str
    alert_id: str
    severity: str
    reason: str
    created_at: str


class CaseDetail(BaseModel):
    metadata: CaseMetadata
    customer: CustomerProfile
    suspicious_transaction: Transaction
    beneficiary: Beneficiary | None
    device: Device | None
    initial_risk_indicators: list[RiskIndicator]
    historical_cases: list[HistoricalCaseSummary]
    current_status: str
    ai_recommendation: str | None = None
    investigation_summary: dict | None = None
    human_review: dict | None = None
    audit_events: list[dict] = []
