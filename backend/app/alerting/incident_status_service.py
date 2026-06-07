from app.core.constants import ALLOWED_INCIDENT_STATUS_TRANSITIONS, IncidentStatus
from app.services.errors import ApiError


class IncidentStatusService:
    def validate_transition(self, current_status: str, target_status: str) -> None:
        current = IncidentStatus(current_status)
        target = IncidentStatus(target_status)
        if target not in ALLOWED_INCIDENT_STATUS_TRANSITIONS[current]:
            raise ApiError(400, "invalid_incident_status_transition", f"Cannot transition incident from {current} to {target}.")
