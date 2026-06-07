from fastapi import APIRouter, Depends

from app.auth.auth_config import get_auth_mode, is_entra_enabled
from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import permissions_for_user
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/mode")
def get_mode() -> dict:
    return {"auth_mode": get_auth_mode(), "entra_enabled": is_entra_enabled()}


@router.get("/me", response_model=AuthenticatedUser)
def get_me(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
    return current_user


@router.get("/permissions")
def get_permissions(current_user: AuthenticatedUser = Depends(get_current_user)) -> dict:
    return {
        "user_id": current_user.user_id,
        "role": current_user.primary_role,
        "permissions": permissions_for_user(current_user),
    }
