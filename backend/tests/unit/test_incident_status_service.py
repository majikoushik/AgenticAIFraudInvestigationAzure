import pytest

from app.alerting.incident_status_service import IncidentStatusService
from app.core.constants import IncidentStatus
from app.services.errors import ApiError


def test_incident_status_service_allows_valid_transition() -> None:
    IncidentStatusService().validate_transition(IncidentStatus.OPEN.value, IncidentStatus.ACKNOWLEDGED.value)


def test_incident_status_service_rejects_invalid_transition() -> None:
    with pytest.raises(ApiError):
        IncidentStatusService().validate_transition(IncidentStatus.CLOSED.value, IncidentStatus.OPEN.value)
