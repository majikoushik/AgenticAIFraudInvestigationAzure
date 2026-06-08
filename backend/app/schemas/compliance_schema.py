from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import ComplianceExportStatus


class ComplianceExportCreateRequest(BaseModel):
    include_audit: bool = True
    include_ai_outputs: bool = True
    include_feedback: bool = True
    redact_pii: bool = True


class ComplianceExportResponse(BaseModel):
    export_id: str
    case_id: str
    status: ComplianceExportStatus
    requested_by: str
    requested_at: datetime
    completed_at: datetime | None = None
    output_path: str | None = None
    manifest: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
