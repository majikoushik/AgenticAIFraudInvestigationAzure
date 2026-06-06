from typing import Any
from datetime import UTC, datetime

from app.repositories.json_repository import JsonRepository


class CaseRepository:
    def __init__(self, json_repository: JsonRepository | None = None) -> None:
        self.json_repository = json_repository or JsonRepository()

    def list_alerts(self) -> list[dict[str, Any]]:
        return self.json_repository.read_list("fraud_alerts.json")

    def get_alert(self, case_id: str) -> dict[str, Any] | None:
        return self._find_by_id(self.list_alerts(), "case_id", case_id)

    def get_case_by_id(self, case_id: str) -> dict[str, Any] | None:
        return self.get_alert(case_id)

    def update_case_status(
        self,
        case_id: str,
        status: str,
        updated_by: str,
        comment: str | None = None,
    ) -> dict[str, Any]:
        alerts = self.list_alerts()
        for alert in alerts:
            if alert.get("case_id") == case_id:
                alert["status"] = status
                alert["status_updated_at"] = datetime.now(UTC).isoformat()
                alert["status_updated_by"] = updated_by
                alert["status_comment"] = comment
                self.json_repository.write_list("fraud_alerts.json", alerts)
                return alert

        raise KeyError(f"Case '{case_id}' was not found.")

    def get_customer(self, customer_id: str) -> dict[str, Any] | None:
        return self._find_by_id(
            self.json_repository.read_list("customers.json"),
            "customer_id",
            customer_id,
        )

    def get_transaction(self, transaction_id: str) -> dict[str, Any] | None:
        return self._find_by_id(
            self.json_repository.read_list("transactions.json"),
            "transaction_id",
            transaction_id,
        )

    def get_beneficiary(self, beneficiary_id: str | None) -> dict[str, Any] | None:
        if beneficiary_id is None:
            return None

        return self._find_by_id(
            self.json_repository.read_list("beneficiaries.json"),
            "beneficiary_id",
            beneficiary_id,
        )

    def get_device(self, device_id: str | None) -> dict[str, Any] | None:
        if device_id is None:
            return None

        return self._find_by_id(
            self.json_repository.read_list("devices.json"),
            "device_id",
            device_id,
        )

    def get_historical_cases(self, customer_id: str) -> list[dict[str, Any]]:
        return [
            case
            for case in self.json_repository.read_list("historical_cases.json")
            if case.get("customer_id") == customer_id
        ]

    @staticmethod
    def _find_by_id(
        records: list[dict[str, Any]],
        field_name: str,
        expected_value: str,
    ) -> dict[str, Any] | None:
        return next(
            (record for record in records if record.get(field_name) == expected_value),
            None,
        )
