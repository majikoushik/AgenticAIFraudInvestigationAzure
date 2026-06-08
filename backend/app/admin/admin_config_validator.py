from typing import Any

from app.admin.admin_config_schema import SAFE_CONFIG_REGISTRY
from app.admin.secret_masking import is_secret_key


class AdminConfigValidator:
    def validate_update(self, key: str, value: Any) -> dict:
        definition = SAFE_CONFIG_REGISTRY.get(key)
        errors = []
        if definition is None:
            return {"key": key, "valid": False, "errors": ["Unknown configuration key."]}
        if not definition.editable:
            errors.append("Configuration item is not editable.")
        if definition.secret or is_secret_key(key):
            errors.append("Secret configuration cannot be updated through the admin panel.")
        if self._looks_like_secret(value):
            errors.append("Value looks like a secret and cannot be stored as non-secret configuration.")
        coerced = self._coerce(value, definition.data_type, errors)
        if definition.allowed_values is not None and coerced not in definition.allowed_values:
            errors.append(f"Value must be one of: {', '.join(str(item) for item in definition.allowed_values)}.")
        if isinstance(coerced, int | float):
            if definition.min_value is not None and coerced < definition.min_value:
                errors.append(f"Value must be >= {definition.min_value}.")
            if definition.max_value is not None and coerced > definition.max_value:
                errors.append(f"Value must be <= {definition.max_value}.")
        if isinstance(coerced, str) and len(coerced) > 256:
            errors.append("String value is too long.")
        return {"key": key, "valid": not errors, "errors": errors, "value": coerced}

    def validate_batch_update(self, updates: list[dict]) -> list[dict]:
        return [self.validate_update(update.get("key", ""), update.get("value")) for update in updates]

    @staticmethod
    def _coerce(value: Any, data_type: str, errors: list[str]):
        try:
            if data_type == "boolean":
                if isinstance(value, bool):
                    return value
                if isinstance(value, str) and value.lower() in {"true", "false"}:
                    return value.lower() == "true"
                errors.append("Value must be boolean.")
                return value
            if data_type == "integer":
                if isinstance(value, bool):
                    raise ValueError
                return int(value)
            if data_type == "float":
                if isinstance(value, bool):
                    raise ValueError
                return float(value)
            if data_type in {"string", "enum"}:
                return str(value)
        except (TypeError, ValueError):
            errors.append(f"Value must be {data_type}.")
        return value

    @staticmethod
    def _looks_like_secret(value: Any) -> bool:
        if not isinstance(value, str):
            return False
        upper = value.upper()
        return any(marker in upper for marker in ["BEGIN PRIVATE KEY", "API_KEY=", "SECRET=", "PASSWORD=", "BEARER "])
