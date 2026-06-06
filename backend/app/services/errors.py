from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class ApiError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


async def api_error_handler(_request: Request, exc: ApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )


async def validation_error_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for error in exc.errors():
        sanitized = dict(error)
        if "ctx" in sanitized:
            sanitized["ctx"] = {key: str(value) for key, value in sanitized["ctx"].items()}
        details.append(sanitized)

    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "details": details,
            }
        },
    )
