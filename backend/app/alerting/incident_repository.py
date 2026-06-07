from app.alerting.alert_config import alerting_config
from app.alerting.json_file_store import JsonFileStore


class IncidentRepository:
    def __init__(self, store: JsonFileStore | None = None) -> None:
        self.store = store or JsonFileStore(alerting_config.incidents_local_store_path)

    def list_incidents(self) -> list[dict]:
        return sorted(self.store.read(), key=lambda item: item.get("created_at", ""), reverse=True)

    def get_incident_by_id(self, incident_id: str) -> dict | None:
        return next((incident for incident in self.list_incidents() if incident.get("incident_id") == incident_id), None)

    def append_incident(self, incident: dict) -> dict:
        incidents = self.store.read()
        incidents.append(incident)
        self.store.write(incidents)
        return incident

    def update_incident(self, incident_id: str, updates: dict) -> dict:
        incidents = self.store.read()
        for incident in incidents:
            if incident.get("incident_id") == incident_id:
                incident.update(updates)
                self.store.write(incidents)
                return incident
        raise KeyError(incident_id)

    def search_incidents(self, severity: str | None = None, status: str | None = None, assigned_to: str | None = None, start_date: str | None = None, end_date: str | None = None) -> list[dict]:
        incidents = self.list_incidents()
        if severity:
            incidents = [incident for incident in incidents if incident.get("severity") == severity]
        if status:
            incidents = [incident for incident in incidents if incident.get("status") == status]
        if assigned_to:
            incidents = [incident for incident in incidents if incident.get("assigned_to") == assigned_to]
        if start_date:
            incidents = [incident for incident in incidents if incident.get("created_at", "") >= start_date]
        if end_date:
            incidents = [incident for incident in incidents if incident.get("created_at", "") <= end_date]
        return incidents
