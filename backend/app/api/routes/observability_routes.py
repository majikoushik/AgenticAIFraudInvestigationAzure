import json
from pathlib import Path

from fastapi import APIRouter, Depends

from app.auth.current_user import AuthenticatedUser
from app.auth.permissions import Permission, require_permission
from app.observability.pii_safe_logging import sanitize_telemetry_properties

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/events")
def recent_telemetry_events(_: AuthenticatedUser = Depends(require_permission(Permission.ADMIN_CONFIG))) -> list[dict]:
    path = Path(__file__).resolve().parents[4] / "data" / "synthetic" / "telemetry_events.json"
    if not path.exists():
        return []
    try:
        events = json.loads(path.read_text(encoding="utf-8") or "[]")
        return [sanitize_telemetry_properties(event) for event in events[-100:]]
    except (OSError, json.JSONDecodeError):
        return []
