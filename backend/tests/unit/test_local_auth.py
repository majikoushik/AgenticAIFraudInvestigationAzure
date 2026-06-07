from fastapi import Request
import pytest

from app.auth.local_auth import get_local_user
from app.services.errors import ApiError


def make_request(headers: dict[str, str] | None = None) -> Request:
    return Request({"type": "http", "headers": [(key.lower().encode(), value.encode()) for key, value in (headers or {}).items()]})


def test_local_auth_returns_default_user_when_headers_missing() -> None:
    user = get_local_user(make_request())

    assert user.user_id == "local_demo_user"
    assert user.primary_role == "FRAUD_ANALYST"


def test_local_auth_reads_demo_headers() -> None:
    user = get_local_user(make_request({"X-Demo-User": "auditor_01", "X-Demo-Role": "AUDITOR", "X-Demo-Email": "auditor@example.com"}))

    assert user.user_id == "auditor_01"
    assert user.primary_role == "AUDITOR"


def test_local_auth_rejects_invalid_role() -> None:
    with pytest.raises(ApiError):
        get_local_user(make_request({"X-Demo-Role": "ROOT"}))
