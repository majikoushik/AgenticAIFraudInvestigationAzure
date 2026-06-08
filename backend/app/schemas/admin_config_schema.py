from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AdminConfigItem(BaseModel):
    key: str
    value: Any
    default_value: Any
    category: str
    data_type: str
    editable: bool
    secret: bool
    description: str
    allowed_values: list[Any] | None = None
    min_value: float | None = None
    max_value: float | None = None
    requires_restart: bool = False
    source: str
    last_updated_at: datetime | None = None
    last_updated_by: str | None = None


class AdminConfigCategory(BaseModel):
    category: str
    items: list[AdminConfigItem]


class AdminConfigResponse(BaseModel):
    categories: list[AdminConfigCategory]
    secret_values_redacted: bool = True


class AdminConfigUpdateItem(BaseModel):
    key: str
    value: Any


class AdminConfigUpdateRequest(BaseModel):
    updates: list[AdminConfigUpdateItem]
    updated_by: str | None = None
    comment: str | None = None


class AdminConfigValidationResult(BaseModel):
    key: str
    valid: bool
    errors: list[str] = Field(default_factory=list)
    value: Any | None = None


class AdminConfigUpdateResponse(BaseModel):
    updated_count: int
    failed_count: int
    updated_items: list[AdminConfigItem]
    validation_errors: list[AdminConfigValidationResult]
    message: str


class AdminConfigHistoryRecord(BaseModel):
    history_id: str
    key: str
    old_value: Any
    new_value: Any
    category: str
    updated_by: str
    updated_at: datetime
    comment: str | None = None
    correlation_id: str | None = None


class FeatureFlag(AdminConfigItem):
    pass


class FeatureFlagUpdateRequest(BaseModel):
    enabled: bool
    comment: str | None = None


class SafeConfigHealthResponse(BaseModel):
    admin_config_enabled: bool
    mode: str
    local_store_accessible: bool
    history_store_accessible: bool
    azure_app_configuration_enabled: bool
    key_vault_enabled: bool
    secret_values_redacted: bool
    editable_config_count: int
    requires_restart_count: int
    allow_runtime_updates: bool
    allow_reset_to_defaults: bool
    require_admin_role: bool
    azure_app_configuration_configured: bool
    key_vault_configured: bool
