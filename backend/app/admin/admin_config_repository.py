import json
from app.alerting.json_file_store import resolve_store_path
from app.admin.admin_config import admin_config_settings
from app.admin.secret_masking import is_secret_key


class AdminConfigRepository:
    def __init__(self, path_text: str | None = None) -> None:
        self.path = resolve_store_path(path_text or admin_config_settings.local_store_path)

    def get_overrides(self) -> dict:
        return self._read().get("overrides", {})

    def get_override(self, key: str):
        return self.get_overrides().get(key)

    def save_overrides(self, overrides: dict) -> dict:
        safe = {key: value for key, value in overrides.items() if not is_secret_key(key)}
        self._write({"overrides": safe})
        return safe

    def update_overrides(self, updates: dict) -> dict:
        overrides = self.get_overrides()
        for key, value in updates.items():
            if not is_secret_key(key):
                overrides[key] = value
        return self.save_overrides(overrides)

    def reset_overrides(self) -> dict:
        return self.save_overrides({})

    def _read(self) -> dict:
        if not self.path.exists():
            self._write({"overrides": {}})
            return {"overrides": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8") or "{}")
            return data if isinstance(data, dict) and isinstance(data.get("overrides", {}), dict) else {"overrides": {}}
        except json.JSONDecodeError:
            return {"overrides": {}}

    def _write(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(f"{self.path.suffix}.tmp")
        temp.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        temp.replace(self.path)
