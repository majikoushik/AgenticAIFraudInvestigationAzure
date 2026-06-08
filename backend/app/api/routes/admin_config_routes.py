from fastapi import APIRouter, Depends, Query

from app.admin.admin_config_service import AdminConfigService
from app.admin.feature_flag_service import FeatureFlagService
from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.schemas.admin_config_schema import (
    AdminConfigCategory,
    AdminConfigHistoryRecord,
    AdminConfigResponse,
    AdminConfigUpdateRequest,
    AdminConfigUpdateResponse,
    FeatureFlag,
    FeatureFlagUpdateRequest,
    SafeConfigHealthResponse,
)

router = APIRouter(prefix="/admin", tags=["admin-config"])
config_service = AdminConfigService()
feature_flag_service = FeatureFlagService(config_service)


@router.get("/config", response_model=AdminConfigResponse)
def get_admin_config(current_user: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return config_service.get_safe_config(actor=current_user.user_id)


@router.patch("/config", response_model=AdminConfigUpdateResponse)
def update_admin_config(request: AdminConfigUpdateRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    updates = [item.model_dump() for item in request.updates]
    return config_service.update_config(updates, updated_by=current_user.user_id, comment=request.comment)


@router.post("/config/reset")
def reset_admin_config(request: dict | None = None, current_user: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return config_service.reset_to_defaults(current_user.user_id, (request or {}).get("comment"))


@router.get("/config/history", response_model=list[AdminConfigHistoryRecord])
def get_admin_config_history(
    key: str | None = None,
    category: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG)),
) -> list[dict]:
    return config_service.get_config_history(key, category, limit)


@router.get("/config/health", response_model=SafeConfigHealthResponse)
def get_admin_config_health(_: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return config_service.get_config_health()


@router.get("/config/{category}", response_model=AdminConfigCategory)
def get_admin_config_category(category: str, _: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return config_service.get_config_by_category(category)


@router.get("/feature-flags", response_model=list[FeatureFlag])
def list_feature_flags(_: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> list[dict]:
    return feature_flag_service.list_feature_flags()


@router.patch("/feature-flags/{flag_key}", response_model=FeatureFlag)
def update_feature_flag(flag_key: str, request: FeatureFlagUpdateRequest, current_user: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> dict:
    return feature_flag_service.update_feature_flag(flag_key, request.enabled, current_user.user_id, request.comment)
