from fastapi import APIRouter

from app.api.routes import (
    agent_routes,
    audit_routes,
    case_routes,
    decision_routes,
    health_routes,
    rag_routes,
    review_routes,
    status_routes,
)

api_router = APIRouter()
api_router.include_router(health_routes.router)
api_router.include_router(case_routes.router, prefix="/api/v1")
api_router.include_router(decision_routes.router, prefix="/api/v1")
api_router.include_router(rag_routes.router, prefix="/api/v1")
api_router.include_router(agent_routes.router, prefix="/api/v1")
api_router.include_router(review_routes.router, prefix="/api/v1")
api_router.include_router(audit_routes.router, prefix="/api/v1")
api_router.include_router(status_routes.router, prefix="/api/v1")
