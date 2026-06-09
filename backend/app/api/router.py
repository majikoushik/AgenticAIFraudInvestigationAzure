from fastapi import APIRouter

from app.api.routes import (
    agent_routes,
    admin_config_routes,
    assignment_routes,
    alert_routes,
    audit_routes,
    auth_routes,
    case_routes,
    compliance_routes,
    cost_routes,
    decision_routes,
    feedback_routes,
    health_routes,
    incident_routes,
    legal_hold_routes,
    metrics_routes,
    notification_routes,
    observability_routes,
    rag_routes,
    readiness_routes,
    review_routes,
    security_routes,
    status_routes,
    retention_routes,
)

api_router = APIRouter()
api_router.include_router(health_routes.router)
api_router.include_router(auth_routes.router, prefix="/api/v1")
api_router.include_router(admin_config_routes.router, prefix="/api/v1")
api_router.include_router(assignment_routes.router, prefix="/api/v1")
api_router.include_router(alert_routes.router, prefix="/api/v1")
api_router.include_router(case_routes.router, prefix="/api/v1")
api_router.include_router(compliance_routes.router, prefix="/api/v1")
api_router.include_router(cost_routes.router, prefix="/api/v1")
api_router.include_router(decision_routes.router, prefix="/api/v1")
api_router.include_router(feedback_routes.router, prefix="/api/v1")
api_router.include_router(feedback_routes.case_router, prefix="/api/v1")
api_router.include_router(rag_routes.router, prefix="/api/v1")
api_router.include_router(agent_routes.router, prefix="/api/v1")
api_router.include_router(metrics_routes.router, prefix="/api/v1")
api_router.include_router(notification_routes.router, prefix="/api/v1")
api_router.include_router(notification_routes.admin_router, prefix="/api/v1")
api_router.include_router(incident_routes.router, prefix="/api/v1")
api_router.include_router(legal_hold_routes.router, prefix="/api/v1")
api_router.include_router(legal_hold_routes.case_router, prefix="/api/v1")
api_router.include_router(observability_routes.router, prefix="/api/v1")
api_router.include_router(review_routes.router, prefix="/api/v1")
api_router.include_router(security_routes.router, prefix="/api/v1")
api_router.include_router(audit_routes.router, prefix="/api/v1")
api_router.include_router(audit_routes.audit_router, prefix="/api/v1")
api_router.include_router(status_routes.router, prefix="/api/v1")
api_router.include_router(retention_routes.router, prefix="/api/v1")
api_router.include_router(readiness_routes.router, prefix="/api/v1")
