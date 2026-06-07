from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IncidentTimelineEvent(BaseModel):
    timestamp: datetime
    actor: str
    action: str
    comment: str


class Incident(BaseModel):
    incident_id: str
    alert_id: str
    title: str
    description: str
    severity: str
    status: str
    assigned_to: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved_by: str | None = None
    resolved_at: datetime | None = None
    closed_by: str | None = None
    closed_at: datetime | None = None
    runbook: str | None = None
    timeline: list[IncidentTimelineEvent] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class IncidentListResponse(BaseModel):
    count: int
    incidents: list[Incident]


class IncidentStatusUpdateRequest(BaseModel):
    target_status: str
    actor: str
    comment: str | None = None


class IncidentAssignRequest(BaseModel):
    assigned_to: str
    actor: str
    comment: str | None = None


class IncidentTimelineRequest(BaseModel):
    actor: str
    action: str
    comment: str


class IncidentCloseRequest(BaseModel):
    actor: str
    comment: str
