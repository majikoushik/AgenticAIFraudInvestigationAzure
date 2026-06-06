from abc import ABC, abstractmethod


class FraudInvestigationAgent(ABC):
    name: str

    @abstractmethod
    def run(self, case_id: str) -> dict:
        raise NotImplementedError
