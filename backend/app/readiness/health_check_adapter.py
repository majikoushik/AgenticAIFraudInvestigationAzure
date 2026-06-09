"""
Health Check Adapter.
Reads available health/config from existing services without tight coupling.
Returns NOT_CHECKED with a warning if a service is unavailable — never fails the full assessment.

SECURITY NOTE: No secrets, tokens, or credentials are returned from any method.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_NOT_CHECKED = {"status": "NOT_CHECKED", "warning": "Service or module unavailable."}


class HealthCheckAdapter:
    """Adapter that reads health state from existing backend services."""

    def get_security_health(self) -> dict:
        try:
            from app.security.secure_config_loader import secure_config_loader
            summary = {
                "secret_provider": secure_config_loader.provider_name
                if hasattr(secure_config_loader, "provider_name")
                else "unknown",
                "key_vault_enabled": False,
            }
            try:
                from app.config import settings
                summary["key_vault_enabled"] = settings.key_vault_enabled
                summary["use_managed_identity"] = settings.use_managed_identity
            except Exception:
                pass
            return {"status": "OK", "details": summary}
        except Exception as exc:
            logger.debug("Security health unavailable: %s", exc)
            return dict(_NOT_CHECKED)

    def get_observability_health(self) -> dict:
        try:
            from app.observability.observability_config import observability_config
            return {
                "status": "OK",
                "details": {
                    "enabled": observability_config.enabled,
                    "mode": observability_config.mode,
                    "azure_connected": observability_config.azure_monitor_enabled
                    if hasattr(observability_config, "azure_monitor_enabled")
                    else False,
                },
            }
        except Exception as exc:
            logger.debug("Observability health unavailable: %s", exc)
            return dict(_NOT_CHECKED)

    def get_rag_health(self) -> dict:
        try:
            from app.config import settings
            return {
                "status": "OK",
                "details": {
                    "azure_search_enabled": settings.feature_enable_azure_search_rag,
                    "search_endpoint_configured": bool(settings.azure_ai_search_endpoint),
                },
            }
        except Exception as exc:
            logger.debug("RAG health unavailable: %s", exc)
            return dict(_NOT_CHECKED)

    def get_agent_provider_health(self) -> dict:
        try:
            from app.config import settings
            return {
                "status": "OK",
                "details": {
                    "ai_provider": settings.ai_provider,
                    "fallback_enabled": settings.ai_provider_allow_fallback,
                    "human_review_required": settings.ai_safety_require_human_review,
                },
            }
        except Exception as exc:
            logger.debug("Agent provider health unavailable: %s", exc)
            return dict(_NOT_CHECKED)

    def get_cost_health(self) -> dict:
        try:
            from app.config import settings
            return {
                "status": "OK",
                "details": {
                    "cost_monitoring_enabled": settings.cost_monitoring_enabled,
                    "daily_budget": settings.cost_daily_budget_limit,
                    "monthly_budget": settings.cost_monthly_budget_limit,
                },
            }
        except Exception as exc:
            logger.debug("Cost health unavailable: %s", exc)
            return dict(_NOT_CHECKED)

    def get_notification_health(self) -> dict:
        try:
            from app.config import settings
            return {
                "status": "OK",
                "details": {
                    "notification_system_enabled": settings.notification_system_enabled,
                    "in_app_enabled": settings.notification_enable_in_app,
                    # Do NOT include webhook URLs or credentials
                },
            }
        except Exception as exc:
            logger.debug("Notification health unavailable: %s", exc)
            return dict(_NOT_CHECKED)

    def get_retention_health(self) -> dict:
        try:
            from app.config import settings
            return {
                "status": "OK",
                "details": {
                    "data_retention_enabled": settings.data_retention_enabled,
                    "purge_dry_run_default": settings.purge_dry_run_default,
                    "legally_reviewed": settings.retention_policy_legally_reviewed,
                },
            }
        except Exception as exc:
            logger.debug("Retention health unavailable: %s", exc)
            return dict(_NOT_CHECKED)

    def get_admin_config_health(self) -> dict:
        try:
            from app.config import settings
            return {
                "status": "OK",
                "details": {
                    "admin_config_enabled": settings.admin_config_enabled,
                    "require_admin_role": settings.admin_config_require_admin_role,
                    "allow_runtime_updates": settings.admin_config_allow_runtime_updates,
                },
            }
        except Exception as exc:
            logger.debug("Admin config health unavailable: %s", exc)
            return dict(_NOT_CHECKED)


# Singleton
health_check_adapter = HealthCheckAdapter()
