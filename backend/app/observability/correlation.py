import contextvars
from uuid import uuid4


_correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("correlation_id", default=None)


def generate_correlation_id() -> str:
    return uuid4().hex


def get_correlation_id() -> str | None:
    return _correlation_id.get()


def set_correlation_id(correlation_id: str) -> None:
    _correlation_id.set(correlation_id)


def clear_correlation_id() -> None:
    _correlation_id.set(None)
