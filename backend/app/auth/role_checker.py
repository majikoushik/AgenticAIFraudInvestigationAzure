from fastapi import Depends

from app.auth.current_user import AuthenticatedUser
from app.services.errors import ApiError


def require_roles(required_roles: list[str]):
    from app.dependencies import get_current_user

    def dependency(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.is_admin() or current_user.has_any_role(required_roles):
            return current_user
        raise ApiError(403, "role_not_allowed", "User role is not allowed for this operation.")

    return dependency
