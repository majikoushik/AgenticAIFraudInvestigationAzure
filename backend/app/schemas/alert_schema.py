from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AlertRule(BaseModel):
    alert_type: str
    severity: str
    title: str
    description: str
    metric_name: str
    threshold_value: float
    recommended_runbook: str


class AlertEvent(BaseModel):
    alert_id: str
    alert_type: str
    severity: str
    title: str
    description: str
    source: str
    status: str = "ACTIVE"
    metric_name: str | None = None
    metric_value: float | None = None
    threshold_value: float | None = None
    case_id: str | None = None
    correlation_id: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    recommended_runbook: str | None = None
    created_at: datetime
    resolved_at: datetime | None = None


class AlertEvaluationResult(BaseModel):
    alert_type: str
    status: str
    alert: AlertEvent | None = None
    reason: str | None = None


class AlertListResponse(BaseModel):
    count: int
    alerts: list[AlertEvent]


class AlertSimulationRequest(BaseModel):
    alert_type: str
    severity: str
    title: str
    description: str


class AlertResolveRequest(BaseModel):
    actor: str
    comment: str | None = None
