from dataclasses import dataclass


@dataclass(frozen=True)
class AuditEventModel:
    audit_id: str
    case_id: str
    event_type: str
    actor: str
    actor_role: str
    timestamp: str
