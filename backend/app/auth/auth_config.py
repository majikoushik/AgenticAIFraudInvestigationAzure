from app.config import settings


VALID_AUTH_MODES = {"local", "entra"}


def get_auth_mode() -> str:
    mode = (settings.auth_mode or "local").strip().lower()
    return mode if mode in VALID_AUTH_MODES else "local"


def is_entra_enabled() -> bool:
    return get_auth_mode() == "entra"
