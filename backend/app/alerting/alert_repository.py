from datetime import datetime, timezone

from app.alerting.alert_config import alerting_config
from app.alerting.json_file_store import JsonFileStore


class AlertRepository:
    def __init__(self, store: JsonFileStore | None = None) -> None:
        self.store = store or JsonFileStore(alerting_config.alerts_local_store_path)

    def list_alerts(self) -> list[dict]:
        return sorted(self.store.read(), key=lambda item: item.get("created_at", ""), reverse=True)

    def get_alert_by_id(self, alert_id: str) -> dict | None:
        return next((alert for alert in self.list_alerts() if alert.get("alert_id") == alert_id), None)

    def append_alert(self, alert: dict) -> dict:
        alerts = self.store.read()
        alerts.append(alert)
        self.store.write(alerts)
        return alert

    def update_alert_status(self, alert_id: str, status: str) -> dict:
        alerts = self.store.read()
        for alert in alerts:
            if alert.get("alert_id") == alert_id:
                alert["status"] = status
                if status == "RESOLVED":
                    alert["resolved_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                self.store.write(alerts)
                return alert
        raise KeyError(alert_id)

    def search_alerts(self, alert_type: str | None = None, severity: str | None = None, status: str | None = None, start_date: str | None = None, end_date: str | None = None) -> list[dict]:
        alerts = self.list_alerts()
        if alert_type:
            alerts = [alert for alert in alerts if alert.get("alert_type") == alert_type]
        if severity:
            alerts = [alert for alert in alerts if alert.get("severity") == severity]
        if status:
            alerts = [alert for alert in alerts if alert.get("status") == status]
        if start_date:
            alerts = [alert for alert in alerts if alert.get("created_at", "") >= start_date]
        if end_date:
            alerts = [alert for alert in alerts if alert.get("created_at", "") <= end_date]
        return alerts
