import copy
import re
from typing import Any


class PiiRedactor:
    sensitive_keys = {"account_number", "authorization", "api_key", "access_token", "refresh_token", "client_secret"}

    def redact_text(self, text: str) -> str:
        redacted = re.sub(r"([A-Za-z0-9._%+-])([A-Za-z0-9._%+-]*)(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", lambda m: f"{m.group(1)}***{m.group(3)}", text)
        redacted = re.sub(r"\b(?:\d[ -]?){13,19}\b", lambda m: self._mask_digits(m.group(0)), redacted)
        redacted = re.sub(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "***-***-****", redacted)
        redacted = re.sub(r"(?i)(api[_-]?key|authorization|bearer|token)\s*[:=]\s*\S+", r"\1=***MASKED***", redacted)
        return redacted

    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        return self._redact(copy.deepcopy(data))

    def _redact(self, value: Any) -> Any:
        if isinstance(value, dict):
            output = {}
            for key, item in value.items():
                if key == "case_id":
                    output[key] = item
                elif key in self.sensitive_keys:
                    output[key] = self._mask_digits(str(item)) if "account" in key else "***MASKED***"
                elif key == "customer_id":
                    output[key] = "***MASKED_CUSTOMER_ID***"
                else:
                    output[key] = self._redact(item)
            return output
        if isinstance(value, list):
            return [self._redact(item) for item in value]
        if isinstance(value, str):
            return self.redact_text(value)
        return value

    @staticmethod
    def _mask_digits(value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if len(digits) <= 4:
            return "****"
        return f"****{digits[-4:]}"


redact_text = PiiRedactor().redact_text
redact_dict = PiiRedactor().redact_dict
