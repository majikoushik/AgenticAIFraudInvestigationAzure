from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass
class InvestigationState:
    case: dict[str, Any]
    outputs: dict[str, Any] = field(default_factory=dict)
    agent_trace: list[dict[str, Any]] = field(default_factory=list)


class StateManager:
    def __init__(self, case: dict[str, Any]) -> None:
        self.state = InvestigationState(case=deepcopy(case))

    def record_agent_output(self, agent_name: str, output: dict[str, Any]) -> None:
        self.state.outputs[agent_name] = output
        self.state.agent_trace.append({"agent": agent_name, "output": output})

    def get_output(self, agent_name: str, default: Any = None) -> Any:
        return self.state.outputs.get(agent_name, default)
