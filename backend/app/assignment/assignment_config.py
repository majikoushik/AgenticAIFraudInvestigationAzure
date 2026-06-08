from pydantic import BaseModel

from app.config import settings


class AssignmentConfig(BaseModel):
    enabled: bool = settings.case_assignment_enabled
    mode: str = settings.case_assignment_mode
    history_store_path: str = settings.assignment_history_store_path
    default_assignment_team: str = settings.default_assignment_team
    default_assignment_priority: str = settings.default_assignment_priority
    sla_hours_by_priority: dict[str, int] = {
        "LOW": settings.sla_low_priority_hours,
        "MEDIUM": settings.sla_medium_priority_hours,
        "HIGH": settings.sla_high_priority_hours,
        "CRITICAL": settings.sla_critical_priority_hours,
    }
    auto_set_sla_on_assignment: bool = settings.auto_set_sla_on_assignment
    allow_self_assignment: bool = settings.allow_self_assignment
    allow_analyst_release_own_case: bool = settings.allow_analyst_release_own_case
    allow_analyst_transfer_request: bool = settings.allow_analyst_transfer_request
    max_active_cases_per_investigator: int = settings.max_active_cases_per_investigator
    workload_high_threshold: int = settings.workload_high_threshold
    workload_critical_threshold: int = settings.workload_critical_threshold

    def safe_summary(self) -> dict:
        return self.model_dump()


assignment_config = AssignmentConfig()
