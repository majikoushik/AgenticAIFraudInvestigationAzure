from app.alerting.alert_service import AlertService


class SimulationService:
    def __init__(self, alert_service: AlertService | None = None) -> None:
        self.alert_service = alert_service or AlertService()

    def simulate_alert(self, alert_type: str, severity: str, title: str, description: str) -> dict:
        alert = self.alert_service.create_alert(
            {
                "alert_type": alert_type,
                "severity": severity,
                "title": title,
                "description": description,
                "source": "simulation",
                "metric_name": "simulation",
                "metric_value": 1,
                "threshold_value": 1,
                "properties": {"simulation": True},
            }
        )
        incidents = self.alert_service.incident_service.list_incidents()
        linked = next((incident for incident in incidents if incident.get("alert_id") == alert.get("alert_id")), None)
        return {"alert": alert, "incident": linked}
