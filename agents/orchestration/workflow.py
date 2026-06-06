from dataclasses import dataclass


@dataclass(frozen=True)
class InvestigationWorkflowResult:
    case_id: str
    recommendation: str
    requires_human_review: bool = True


class InvestigationWorkflow:
    """Deterministic placeholder for future multi-agent orchestration."""

    def run(self, case_id: str) -> InvestigationWorkflowResult:
        return InvestigationWorkflowResult(
            case_id=case_id,
            recommendation="Review synthetic evidence before taking any action.",
        )
