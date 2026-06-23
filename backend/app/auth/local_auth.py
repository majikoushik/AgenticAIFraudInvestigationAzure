from fastapi import Request

from app.auth.current_user import AuthenticatedUser
from app.core.constants import ReviewerRole
from app.services.errors import ApiError


DEFAULT_LOCAL_USER = {
    "user_id": "local_demo_user",
    "display_name": "Local Demo User",
    "email": "local_demo_user@example.com",
    "role": ReviewerRole.FRAUD_ANALYST.value,
}


def get_local_user(request: Request) -> AuthenticatedUser:
    from app.config import settings
    # Development-only fallback. Do not use local auth mode in production.
    if settings.deployment_mode.lower() in ["prod", "production"]:
        raise ApiError(500, "auth_configuration_error", "Local demo auth is not allowed in production mode.")

    user_id = request.headers.get("X-Demo-User") or DEFAULT_LOCAL_USER["user_id"]
    role = request.headers.get("X-Demo-Role") or DEFAULT_LOCAL_USER["role"]
    email = request.headers.get("X-Demo-Email") or DEFAULT_LOCAL_USER["email"]

    try:
        normalized_role = ReviewerRole(role.strip().upper()).value
    except ValueError as exc:
        raise ApiError(403, "invalid_demo_role", f"Invalid demo role '{role}'.") from exc

    if normalized_role in {ReviewerRole.SYSTEM.value, ReviewerRole.UNKNOWN.value}:
        raise ApiError(403, "invalid_demo_role", f"Invalid demo role '{role}'.")

    return AuthenticatedUser(
        user_id=user_id,
        display_name=user_id.replace("_", " ").title(),
        email=email,
        roles=[normalized_role],
        primary_role=normalized_role,
        auth_mode="local",
    )
