from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import AssignmentPriority, AssignmentStatus, SlaStatus


class AssignmentFields(BaseModel):
    assigned_to: str | None = None
    assigned_to_name: str | None = None
    assigned_to_role: str | None = None
    assigned_team: str | None = "Fraud Operations"
    assigned_by: str | None = None
    assigned_at: datetime | None = None
    assignment_status: AssignmentStatus = AssignmentStatus.UNASSIGNED
    assignment_priority: AssignmentPriority = AssignmentPriority.MEDIUM
    sla_due_at: datetime | None = None
    sla_status: SlaStatus = SlaStatus.NOT_APPLICABLE
    last_assignment_action: str | None = None


class CaseAssignmentRequest(BaseModel):
    case_id: str | None = None
    assigned_to: str
    assigned_to_name: str
    assigned_to_role: str
    assigned_team: str = "Fraud Operations"
    assignment_priority: AssignmentPriority = AssignmentPriority.MEDIUM
    sla_due_at: datetime | None = None
    comment: str | None = None


class CaseReassignmentRequest(BaseModel):
    assigned_to: str
    assigned_to_name: str
    assigned_to_role: str
    assigned_team: str = "Fraud Operations"
    assignment_priority: AssignmentPriority | None = None
    sla_due_at: datetime | None = None
    comment: str | None = None


class CaseAcceptRequest(BaseModel):
    accepted_by: str
    comment: str | None = None


class CaseReleaseRequest(BaseModel):
    released_by: str
    reason: str
    comment: str | None = None


class CaseTransferRequest(BaseModel):
    assigned_to: str
    assigned_to_name: str
    assigned_to_role: str
    assigned_team: str = "Fraud Operations"
    comment: str | None = None


class AssignmentResponse(BaseModel):
    case_id: str
    message: str
    assignment: AssignmentFields
    case: dict[str, Any]


class AssignmentHistoryRecord(BaseModel):
    history_id: str
    case_id: str
    action: str
    previous_assigned_to: str | None = None
    new_assigned_to: str | None = None
    actor: str
    actor_role: str
    comment: str | None = None
    timestamp: datetime


class QueueCase(BaseModel):
    case_id: str
    alert_id: str
    alert_type: str
    risk_level: str
    case_status: str
    assignment_status: AssignmentStatus
    assigned_to: str | None = None
    assigned_to_name: str | None = None
    assigned_team: str | None = None
    assignment_priority: AssignmentPriority
    sla_status: SlaStatus
    sla_due_at: datetime | None = None
    created_at: str
    reason: str


class QueueResponse(BaseModel):
    queue_name: str
    count: int
    cases: list[QueueCase]
    filters: dict[str, Any] = Field(default_factory=dict)


InvestigatorQueueResponse = QueueResponse
TeamQueueResponse = QueueResponse
UnassignedQueueResponse = QueueResponse


class InvestigatorWorkload(BaseModel):
    user_id: str
    display_name: str
    role: str
    team: str
    active_case_count: int
    accepted_case_count: int
    cases_by_priority: dict[str, int]
    workload_status: str


class WorkloadSummaryResponse(BaseModel):
    total_assigned_cases: int
    total_unassigned_cases: int
    active_cases_by_investigator: dict[str, int]
    cases_by_priority: dict[str, int]
    cases_by_sla_status: dict[str, int]
    overloaded_investigators: list[InvestigatorWorkload]
    available_investigators: list[InvestigatorWorkload]
    average_cases_per_investigator: float


class AssignmentMetricsResponse(WorkloadSummaryResponse):
    total_accepted_cases: int
    total_released_cases: int
    cases_by_team: dict[str, int]
    overloaded_investigator_count: int
    sla_breached_case_count: int
    sla_at_risk_case_count: int
