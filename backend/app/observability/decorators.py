from functools import wraps
from time import perf_counter

from app.observability.telemetry_client import get_telemetry_client


def track_operation(operation_name: str, category: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            started = perf_counter()
            client = get_telemetry_client()
            try:
                result = func(*args, **kwargs)
                client.track_event(f"{category.upper()}_{operation_name}_COMPLETED", {"operation": operation_name, "category": category}, {"duration_ms": (perf_counter() - started) * 1000})
                return result
            except Exception as exc:
                client.track_exception(exc, {"operation": operation_name, "category": category})
                raise
        return wrapper
    return decorator


def track_agent_execution(agent_name: str):
    return track_operation(agent_name, "agent")


def track_rag_retrieval(index_name: str | None = None):
    return track_operation(index_name or "rag_retrieval", "rag")


def track_llm_call(provider: str | None = None):
    return track_operation(provider or "llm_call", "llm")
