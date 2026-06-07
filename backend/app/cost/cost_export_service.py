import csv
from io import StringIO

from app.cost.cost_service import CostService


class CostExportService:
    def __init__(self, service: CostService | None = None) -> None:
        self.service = service or CostService()

    def export_cost_summary_csv(self) -> str:
        summary = self.service.get_cost_summary()
        return self._csv_from_rows([summary])

    def export_token_usage_csv(self) -> str:
        rows = self.service.repository.list_token_usage_records()
        return self._csv_from_rows(rows)

    def export_case_cost_breakdown_csv(self, case_id: str) -> str:
        breakdown = self.service.get_case_cost_breakdown(case_id)
        return self._csv_from_rows(breakdown["cost_records"])

    @staticmethod
    def _csv_from_rows(rows: list[dict]) -> str:
        if not rows:
            return ""
        output = StringIO()
        fieldnames = sorted({key for row in rows for key in row.keys() if key != "metadata"})
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()
