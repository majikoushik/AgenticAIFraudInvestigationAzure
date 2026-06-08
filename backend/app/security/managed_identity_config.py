from dataclasses import dataclass

from app.config import settings


@dataclass(frozen=True)
class ManagedIdentityConfig:
    use_managed_identity: bool = settings.use_managed_identity
    azure_client_id: str = settings.azure_client_id

    @property
    def user_assigned_identity_configured(self) -> bool:
        return bool(self.azure_client_id)

    def safe_summary(self) -> dict:
        return {
            "use_managed_identity": self.use_managed_identity,
            "user_assigned_identity_configured": self.user_assigned_identity_configured,
        }


managed_identity_config = ManagedIdentityConfig()
