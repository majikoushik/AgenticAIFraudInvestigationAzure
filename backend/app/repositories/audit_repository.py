import json
import os
from pathlib import Path

from app.config import get_synthetic_data_path


class AuditRepository:
    def __init__(self, file_path: str | Path | None = None) -> None:
        self.file_path = Path(file_path) if file_path else get_synthetic_data_path() / "audit_events.json"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text("[]", encoding="utf-8")

    def list_all_events(self) -> list[dict]:
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            return sorted(data, key=lambda event: event.get("timestamp", ""))
        except (json.JSONDecodeError, OSError):
            return []

    def list_events_by_case_id(self, case_id: str) -> list[dict]:
        return [event for event in self.list_all_events() if event.get("case_id") == case_id]

    def append_event(self, event: dict) -> dict:
        events = self.list_all_events()
        events.append(event)
        self._atomic_write(events)
        return event

    def search_events(
        self,
        case_id: str | None = None,
        event_type: str | None = None,
        actor: str | None = None,
        actor_role: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict]:
        events = self.list_all_events()
        if case_id:
            events = [event for event in events if event.get("case_id") == case_id]
        if event_type:
            events = [event for event in events if event.get("event_type") == event_type]
        if actor:
            events = [event for event in events if event.get("actor") == actor]
        if actor_role:
            events = [event for event in events if event.get("actor_role") == actor_role]
        if start_date:
            events = [event for event in events if event.get("timestamp", "") >= start_date]
        if end_date:
            events = [event for event in events if event.get("timestamp", "") <= end_date]
        return sorted(events, key=lambda event: event.get("timestamp", ""))

    def replace_all(self, events: list[dict]) -> None:
        self._atomic_write(events)

    def _atomic_write(self, events: list[dict]) -> None:
        temp_path = self.file_path.with_suffix(f"{self.file_path.suffix}.tmp")
        temp_path.write_text(json.dumps(events, indent=2), encoding="utf-8")
        os.replace(temp_path, self.file_path)
