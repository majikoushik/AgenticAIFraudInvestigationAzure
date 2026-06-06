from pydantic import BaseModel


class RiskIndicator(BaseModel):
    code: str
    description: str
    severity: str


class HistoricalCaseSummary(BaseModel):
    case_id: str
    outcome: str
    summary: str


class AuditEntry(BaseModel):
    case_id: str
    action: str
    decision: str | None = None
    comment: str | None = None
    reviewed_by: str | None = None
    created_at: str


class AuditTrailResponse(BaseModel):
    case_id: str
    entries: list[AuditEntry]
