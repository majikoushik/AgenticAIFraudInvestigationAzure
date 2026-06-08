from collections import Counter, defaultdict
from statistics import mean
from typing import Any

from app.assignment.assignment_config import assignment_config
from app.assignment.assignment_repository import AssignmentRepository
from app.core.constants import AssignmentStatus
from app.repositories.json_repository import JsonRepository


class WorkloadService:
    def __init__(self, repository: AssignmentRepository | None = None, json_repository: JsonRepository | None = None) -> None:
        self.repository = repository or AssignmentRepository()
        self.json_repository = json_repository or JsonRepository()
        self.config = assignment_config

    def get_workload_summary(self) -> dict[str, Any]:
        cases = self.repository.list_cases()
        assigned_cases = [case for case in cases if case.get("assigned_to")]
        workloads = self._build_workloads(assigned_cases)
        return {
            "total_assigned_cases": len(assigned_cases),
            "total_unassigned_cases": len([case for case in cases if not case.get("assigned_to")]),
            "active_cases_by_investigator": dict(Counter(case.get("assigned_to") for case in assigned_cases if case.get("assigned_to"))),
            "cases_by_priority": dict(Counter(case.get("assignment_priority") for case in cases if case.get("assignment_priority"))),
            "cases_by_sla_status": dict(Counter(case.get("sla_status") for case in cases if case.get("sla_status"))),
            "overloaded_investigators": [item for item in workloads if item["workload_status"] in {"HIGH", "CRITICAL"}],
            "available_investigators": [item for item in workloads if item["workload_status"] == "AVAILABLE"],
            "average_cases_per_investigator": round(mean([item["active_case_count"] for item in workloads]), 2) if workloads else 0.0,
        }

    def get_investigator_workload(self, user_id: str) -> dict[str, Any]:
        return next((item for item in self._build_workloads(self.repository.list_cases()) if item["user_id"] == user_id), self._empty_user(user_id))

    def get_team_workload(self, team: str | None = None) -> dict[str, Any]:
        workloads = self._build_workloads(self.repository.list_cases())
        if team:
            workloads = [item for item in workloads if item["team"].lower() == team.lower()]
        return {"team": team, "investigators": workloads}

    def get_recommended_investigators(self, limit: int = 5) -> list[dict[str, Any]]:
        return sorted(self._build_workloads(self.repository.list_cases()), key=lambda item: item["active_case_count"])[:limit]

    def get_assignment_metrics(self) -> dict[str, Any]:
        summary = self.get_workload_summary()
        cases = self.repository.list_cases()
        return {
            **summary,
            "total_accepted_cases": len([case for case in cases if case.get("assignment_status") == AssignmentStatus.ACCEPTED.value]),
            "total_released_cases": len([case for case in cases if case.get("assignment_status") == AssignmentStatus.RELEASED.value]),
            "cases_by_team": dict(Counter(case.get("assigned_team") for case in cases if case.get("assigned_team"))),
            "overloaded_investigator_count": len(summary["overloaded_investigators"]),
            "sla_breached_case_count": summary["cases_by_sla_status"].get("BREACHED", 0),
            "sla_at_risk_case_count": summary["cases_by_sla_status"].get("AT_RISK", 0),
        }

    def _build_workloads(self, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
        demo_users = {user["user_id"]: user for user in self._demo_users()}
        assigned_cases = [case for case in cases if case.get("assigned_to")]
        for case in assigned_cases:
            demo_users.setdefault(case["assigned_to"], {
                "user_id": case["assigned_to"],
                "display_name": case.get("assigned_to_name") or case["assigned_to"],
                "role": case.get("assigned_to_role") or "FRAUD_ANALYST",
                "team": case.get("assigned_team") or self.config.default_assignment_team,
                "active": True,
            })
        by_user = defaultdict(list)
        for case in assigned_cases:
            by_user[case["assigned_to"]].append(case)
        return [
            self._workload_for_user(user, by_user.get(user_id, []))
            for user_id, user in sorted(demo_users.items())
            if user.get("active", True)
        ]

    def _workload_for_user(self, user: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
        count = len(cases)
        if count >= self.config.workload_critical_threshold:
            status = "CRITICAL"
        elif count >= self.config.workload_high_threshold:
            status = "HIGH"
        else:
            status = "AVAILABLE"
        return {
            "user_id": user["user_id"],
            "display_name": user.get("display_name") or user["user_id"],
            "role": user.get("role") or "FRAUD_ANALYST",
            "team": user.get("team") or self.config.default_assignment_team,
            "active_case_count": count,
            "accepted_case_count": len([case for case in cases if case.get("assignment_status") == AssignmentStatus.ACCEPTED.value]),
            "cases_by_priority": dict(Counter(case.get("assignment_priority") for case in cases if case.get("assignment_priority"))),
            "workload_status": status,
        }

    def _demo_users(self) -> list[dict[str, Any]]:
        users = self.json_repository.read_list("investigators.json")
        if users:
            return users
        return [
            {"user_id": "fraud_analyst_01", "display_name": "Fraud Analyst 01", "role": "FRAUD_ANALYST", "team": "Fraud Operations", "active": True},
            {"user_id": "fraud_analyst_02", "display_name": "Fraud Analyst 02", "role": "FRAUD_ANALYST", "team": "Fraud Operations", "active": True},
            {"user_id": "compliance_officer_01", "display_name": "Compliance Officer 01", "role": "COMPLIANCE_OFFICER", "team": "Compliance Review", "active": True},
        ]

    @staticmethod
    def _empty_user(user_id: str) -> dict[str, Any]:
        return {"user_id": user_id, "display_name": user_id, "role": "FRAUD_ANALYST", "team": "Fraud Operations", "active_case_count": 0, "accepted_case_count": 0, "cases_by_priority": {}, "workload_status": "AVAILABLE"}
