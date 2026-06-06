from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import settings
from app.services.errors import ApiError, api_error_handler, validation_error_handler
from fastapi.exceptions import RequestValidationError

app = FastAPI(
    title="Agentic AI Fraud Investigation Backend",
    version="0.1.0",
    description="MVP FastAPI service for fraud investigation workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.include_router(api_router)
