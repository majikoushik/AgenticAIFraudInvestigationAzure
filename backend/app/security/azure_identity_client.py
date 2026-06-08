import logging

from app.security.managed_identity_config import managed_identity_config

logger = logging.getLogger(__name__)


def get_azure_credential():
    try:
        if managed_identity_config.use_managed_identity:
            from azure.identity import ManagedIdentityCredential

            kwargs = {"client_id": managed_identity_config.azure_client_id} if managed_identity_config.azure_client_id else {}
            return ManagedIdentityCredential(**kwargs)
        from azure.identity import DefaultAzureCredential

        return DefaultAzureCredential(exclude_interactive_browser_credential=True)
    except Exception:
        logger.warning("Azure credential could not be initialized.")
        return None


def credential_available() -> bool:
    return get_azure_credential() is not None


def get_identity_summary() -> dict:
    return {
        **managed_identity_config.safe_summary(),
        "credential_available": credential_available(),
    }
