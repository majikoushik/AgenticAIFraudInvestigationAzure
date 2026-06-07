from fastapi import Request

from app.auth.auth_config import get_auth_mode
from app.auth.current_user import AuthenticatedUser
from app.auth.jwt_validator import validate_entra_request
from app.auth.local_auth import get_local_user


def get_current_user(request: Request) -> AuthenticatedUser:
    mode = get_auth_mode()
    if mode == "local":
        return get_local_user(request)
    return validate_entra_request(request)
