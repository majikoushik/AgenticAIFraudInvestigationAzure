from time import perf_counter

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.observability import telemetry_events as events
from app.observability.correlation import clear_correlation_id, generate_correlation_id, set_correlation_id
from app.observability.observability_config import observability_config
from app.observability.telemetry_client import get_telemetry_client


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or generate_correlation_id()
        set_correlation_id(correlation_id)
        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            clear_correlation_id()


class ApiTelemetryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not observability_config.enable_api:
            return await call_next(request)

        client = get_telemetry_client()
        path = request.url.path
        method = request.method
        started = perf_counter()
        client.track_event(events.API_REQUEST_STARTED, {"path": path, "method": method})
        try:
            response = await call_next(request)
            duration_ms = round((perf_counter() - started) * 1000, 2)
            props = {"path": path, "method": method, "status_code": response.status_code, "success": response.status_code < 500}
            client.track_event(events.API_REQUEST_COMPLETED, props, {"duration_ms": duration_ms})
            if response.status_code == 401:
                client.track_event(events.AUTHENTICATION_FAILED, props)
            if response.status_code == 403:
                client.track_event(events.AUTHORIZATION_FAILED, props)
            return response
        except Exception as exc:
            duration_ms = round((perf_counter() - started) * 1000, 2)
            client.track_event(events.API_REQUEST_FAILED, {"path": path, "method": method, "error_type": type(exc).__name__}, {"duration_ms": duration_ms})
            client.track_exception(exc, {"path": path, "method": method})
            raise
