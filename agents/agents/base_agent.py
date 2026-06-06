from abc import ABC, abstractmethod
from typing import Any

from agents.orchestration.state_manager import InvestigationState


class BaseAgent(ABC):
    name: str

    @abstractmethod
    def run(self, state: InvestigationState) -> dict[str, Any]:
        raise NotImplementedError
