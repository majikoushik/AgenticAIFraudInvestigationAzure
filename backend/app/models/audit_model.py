from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AuditEventModel:
    audit_id: str
    case_id: str | None
    event_type: str
    event_category: str
    actor: str
    actor_role: str
    action: str
    description: str
    timestamp: str
    metadata: dict[str, Any] = field(default_factory=dict)
