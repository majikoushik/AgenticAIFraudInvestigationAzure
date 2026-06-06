from datetime import datetime

from pydantic import BaseModel, Field


class CaseStatusResponse(BaseModel):
    case_id: str
    status: str
    allowed_next_statuses: list[str]
    status_updated_at: datetime | None = None
    status_updated_by: str | None = None
    status_comment: str | None = None


class CaseStatusUpdateRequest(BaseModel):
    target_status: str
    actor: str = Field(default="system", min_length=1)
    actor_role: str = Field(default="SYSTEM", min_length=1)
    comment: str | None = None


class CaseStatusUpdateResponse(BaseModel):
    case_id: str
    previous_status: str
    new_status: str
    allowed_next_statuses: list[str]
    message: str
