from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.core.constants import DataCategory, DataClassification, LegalHoldStatus, RetentionAction, RetentionStatus


class RetentionPolicy(BaseModel):
    policy_id: str
    data_category: DataCategory
    classification: DataClassification
    retention_days: int
    archive_after_days: int
    purge_after_days: int
    auto_archive: bool = False
    auto_purge: bool = False
    requires_approval_for_archive: bool = False
    requires_approval_for_purge: bool = True
    legal_hold_exempt: bool = False
    allow_purge: bool = True
    description: str
    enabled: bool = True
    last_updated_by: str = "system"
    last_updated_at: datetime
    warnings: list[str] = Field(default_factory=list)


class RetentionPolicyUpdateRequest(BaseModel):
    retention_days: int | None = None
    archive_after_days: int | None = None
    purge_after_days: int | None = None
    auto_archive: bool | None = None
    auto_purge: bool | None = None
    requires_approval_for_archive: bool | None = None
    requires_approval_for_purge: bool | None = None
    legal_hold_exempt: bool | None = None
    allow_purge: bool | None = None
    description: str | None = None
    enabled: bool | None = None


class RetentionMetadata(BaseModel):
    data_category: DataCategory
    classification: DataClassification
    created_at: datetime
    retention_policy_id: str
    retention_status: RetentionStatus = RetentionStatus.ACTIVE
    archive_eligible_at: datetime
    purge_eligible_at: datetime
    legal_hold_status: LegalHoldStatus = LegalHoldStatus.NONE
    legal_hold_id: str | None = None
    last_retention_scan_at: datetime | None = None


class RetentionScanRequest(BaseModel):
    data_category: DataCategory | None = None
    dry_run: bool = True


class RetentionCandidate(BaseModel):
    record_id: str
    data_category: DataCategory
    classification: DataClassification
    created_at: datetime | None = None
    retention_status: RetentionStatus
    recommended_action: RetentionAction
    reason: str
    legal_hold_status: LegalHoldStatus = LegalHoldStatus.NONE
    days_until_purge: int | None = None
    source_file: str
    case_id: str | None = None


class RetentionScanResult(BaseModel):
    scan_id: str
    dry_run: bool
    started_at: datetime
    completed_at: datetime | None = None
    categories_scanned: int = 0
    records_scanned: int = 0
    archive_candidates: int = 0
    purge_candidates: int = 0
    legal_hold_records: int = 0
    review_required: int = 0
    errors: list[str] = Field(default_factory=list)
    candidates: list[RetentionCandidate] = Field(default_factory=list)


class RetentionActionRequest(BaseModel):
    scan_id: str | None = None
    record_ids: list[str] | None = None
    data_category: DataCategory | None = None
    dry_run: bool = True
    approved_by: str | None = None
    approval_id: str | None = None


class RetentionActionResponse(BaseModel):
    action: RetentionAction
    dry_run: bool
    requested_by: str
    processed_count: int
    blocked_count: int = 0
    results: list[dict[str, Any]] = Field(default_factory=list)


class RetentionReviewQueueResponse(BaseModel):
    count: int
    candidates: list[RetentionCandidate]
