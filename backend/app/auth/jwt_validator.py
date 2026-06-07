import json
import urllib.request
from functools import lru_cache

from fastapi import Request

from app.auth.current_user import AuthenticatedUser
from app.config import settings
from app.core.constants import ReviewerRole
from app.services.errors import ApiError


ENTRA_ROLE_MAP = {
    "Fraud.Analyst": "FRAUD_ANALYST",
    "Fraud.Manager": "FRAUD_MANAGER",
    "Compliance.Officer": "COMPLIANCE_OFFICER",
    "Auditor": "AUDITOR",
    "Admin": "ADMIN",
}


def validate_entra_request(request: Request) -> AuthenticatedUser:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise ApiError(401, "missing_token", "Bearer access token is required.")
    return validate_entra_token(auth_header.removeprefix("Bearer ").strip())


def validate_entra_token(token: str) -> AuthenticatedUser:
    if not token:
        raise ApiError(401, "missing_token", "Bearer access token is required.")
    try:
        from jose import jwt
    except ImportError as exc:
        raise ApiError(500, "jwt_dependency_missing", "JWT validation dependency is not installed.") from exc

    issuer = f"https://login.microsoftonline.com/{settings.entra_tenant_id}/v2.0"
    audience = settings.entra_api_audience or settings.entra_client_id
    if not settings.entra_tenant_id or not audience:
        raise ApiError(500, "entra_not_configured", "Entra ID authentication is not configured.")

    try:
        claims = jwt.decode(
            token,
            get_jwks(),
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
            options={"verify_nbf": True},
        )
    except Exception as exc:
        raise ApiError(401, "invalid_token", "Access token validation failed.") from exc

    roles = [_map_role(role) for role in claims.get("roles", [])]
    roles = [role for role in roles if role]
    if not roles:
        if settings.entra_allow_default_role:
            roles = [ReviewerRole.FRAUD_ANALYST.value]
        else:
            raise ApiError(403, "roles_missing", "Access token does not contain an allowed application role.")

    return AuthenticatedUser(
        user_id=claims.get("oid") or claims.get("sub"),
        display_name=claims.get("name"),
        email=claims.get("preferred_username") or claims.get("email"),
        roles=roles,
        primary_role=roles[0],
        auth_mode="entra",
        tenant_id=claims.get("tid"),
        token_subject=claims.get("sub"),
    )


@lru_cache(maxsize=1)
def get_jwks() -> dict:
    authority = settings.entra_authority or f"https://login.microsoftonline.com/{settings.entra_tenant_id}"
    metadata_url = f"{authority.rstrip('/')}/v2.0/.well-known/openid-configuration"
    with urllib.request.urlopen(metadata_url, timeout=10) as response:
        metadata = json.loads(response.read().decode("utf-8"))
    with urllib.request.urlopen(metadata["jwks_uri"], timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _map_role(role: str) -> str | None:
    mapped = ENTRA_ROLE_MAP.get(role, role)
    try:
        normalized = ReviewerRole(mapped.strip().upper()).value
    except ValueError:
        return None
    return normalized if normalized not in {ReviewerRole.SYSTEM.value, ReviewerRole.UNKNOWN.value} else None
