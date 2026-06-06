from app.repositories.case_repository import CaseRepository
from app.schemas.beneficiary_schema import Beneficiary
from app.schemas.customer_schema import CustomerProfile
from app.schemas.device_schema import Device
from app.schemas.evidence_schema import HistoricalCaseSummary, RiskIndicator
from app.schemas.transaction_schema import Transaction
from app.services.errors import ApiError


class EvidenceService:
    def __init__(self, repository: CaseRepository) -> None:
        self.repository = repository

    def build_customer_profile(self, customer_id: str) -> CustomerProfile:
        customer = self.repository.get_customer(customer_id)
        if customer is None:
            raise ApiError(404, "customer_not_found", "Customer profile was not found.")

        return CustomerProfile(
            customer_id=customer["customer_id"],
            display_name=customer["display_name"],
            account_number_masked=self._mask_account_number(customer["account_number"]),
            segment=customer["segment"],
            risk_tier=customer["risk_tier"],
            home_country=customer["home_country"],
            account_opened_date=customer["account_opened_date"],
            average_transaction_amount=customer["average_transaction_amount"],
        )

    def build_transaction(self, transaction_id: str) -> Transaction:
        transaction = self.repository.get_transaction(transaction_id)
        if transaction is None:
            raise ApiError(404, "transaction_not_found", "Suspicious transaction was not found.")

        return Transaction(**transaction)

    def build_beneficiary(self, beneficiary_id: str | None) -> Beneficiary | None:
        beneficiary = self.repository.get_beneficiary(beneficiary_id)
        return Beneficiary(**beneficiary) if beneficiary else None

    def build_device(self, device_id: str | None) -> Device | None:
        device = self.repository.get_device(device_id)
        return Device(**device) if device else None

    def build_risk_indicators(self, indicators: list[dict[str, str]]) -> list[RiskIndicator]:
        return [RiskIndicator(**indicator) for indicator in indicators]

    def build_historical_cases(self, customer_id: str) -> list[HistoricalCaseSummary]:
        return [
            HistoricalCaseSummary(**historical_case)
            for historical_case in self.repository.get_historical_cases(customer_id)
        ]

    @staticmethod
    def _mask_account_number(account_number: str) -> str:
        return f"****{account_number[-4:]}" if len(account_number) > 4 else "****"
