"""
Readiness configuration loader.
Reads readiness settings from the main Settings object and exposes a safe summary
that never includes secrets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.config import settings, get_synthetic_data_path


@dataclass
class ReadinessConfig:
    """Runtime configuration for the production readiness framework."""

    enabled: bool = True
    mode: str = "local"
    assessment_store_path: str = "data/synthetic/readiness_assessments.json"
    risk_register_store_path: str = "data/synthetic/readiness_risk_register.json"
    report_export_path: str = "data/exports/readiness"
    require_admin_role: bool = True
    min_score_for_ready: float = 90.0
    max_blockers_for_ready: int = 0
    max_high_risks_for_ready_with_risks: int = 3
    enable_static_file_checks: bool = True
    enable_health_endpoint_checks: bool = True
    enable_config_checks: bool = True
    enable_security_checks: bool = True
    enable_test_coverage_checks: bool = False
    default_environment: str = "dev"
    target_environment: str = "prod"

    def resolved_assessment_store_path(self) -> Path:
        p = Path(self.assessment_store_path)
        if p.is_absolute():
            return p
        base = Path(__file__).resolve().parents[3]
        return (base / p).resolve()

    def resolved_risk_register_store_path(self) -> Path:
        p = Path(self.risk_register_store_path)
        if p.is_absolute():
            return p
        base = Path(__file__).resolve().parents[3]
        return (base / p).resolve()

    def resolved_report_export_path(self) -> Path:
        p = Path(self.report_export_path)
        if p.is_absolute():
            return p
        base = Path(__file__).resolve().parents[3]
        return (base / p).resolve()

    def safe_summary(self) -> dict:
        """Return a safe summary of the config — no secrets exposed."""
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "require_admin_role": self.require_admin_role,
            "min_score_for_ready": self.min_score_for_ready,
            "max_blockers_for_ready": self.max_blockers_for_ready,
            "max_high_risks_for_ready_with_risks": self.max_high_risks_for_ready_with_risks,
            "enable_static_file_checks": self.enable_static_file_checks,
            "enable_health_endpoint_checks": self.enable_health_endpoint_checks,
            "enable_config_checks": self.enable_config_checks,
            "enable_security_checks": self.enable_security_checks,
            "enable_test_coverage_checks": self.enable_test_coverage_checks,
            "default_environment": self.default_environment,
            "target_environment": self.target_environment,
        }


def _build_readiness_config() -> ReadinessConfig:
    return ReadinessConfig(
        enabled=settings.production_readiness_enabled,
        mode=settings.production_readiness_mode,
        assessment_store_path=settings.readiness_assessment_store_path,
        risk_register_store_path=settings.readiness_risk_register_store_path,
        report_export_path=settings.readiness_report_export_path,
        require_admin_role=settings.readiness_require_admin_role,
        min_score_for_ready=settings.readiness_min_score_for_ready,
        max_blockers_for_ready=settings.readiness_max_blockers_for_ready,
        max_high_risks_for_ready_with_risks=settings.readiness_max_high_risks_for_ready_with_risks,
        enable_static_file_checks=settings.readiness_enable_static_file_checks,
        enable_health_endpoint_checks=settings.readiness_enable_health_endpoint_checks,
        enable_config_checks=settings.readiness_enable_config_checks,
        enable_security_checks=settings.readiness_enable_security_checks,
        enable_test_coverage_checks=settings.readiness_enable_test_coverage_checks,
        default_environment=settings.readiness_default_environment,
        target_environment=settings.readiness_target_environment,
    )


# Singleton config instance
readiness_config: ReadinessConfig = _build_readiness_config()
