from abc import ABC, abstractmethod


class BaseSecretProvider(ABC):
    @abstractmethod
    def get_secret(self, logical_key: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def get_secret_by_name(self, secret_name: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def provider_name(self) -> str:
        raise NotImplementedError
