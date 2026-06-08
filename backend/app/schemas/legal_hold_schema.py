from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import DataCategory, LegalHoldStatus


class LegalHoldCreateRequest(BaseModel):
    case_id: str | None = None
    record_id: str | None = None
    data_category: DataCategory | None = None
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class LegalHoldReleaseRequest(BaseModel):
    release_reason: str


class LegalHoldResponse(BaseModel):
    legal_hold_id: str
    case_id: str | None = None
    record_id: str | None = None
    data_category: DataCategory | None = None
    reason: str
    created_by: str
    created_at: datetime
    status: LegalHoldStatus
    released_by: str | None = None
    released_at: datetime | None = None
    release_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
