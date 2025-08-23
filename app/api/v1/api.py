"""
Main API router for v1 endpoints.

This module aggregates all v1 API routes and provides the main entry point
for the API version 1.
"""

from fastapi import APIRouter

# Import route modules
from app.api.v1.endpoints import workspace

api_router = APIRouter()

# Include route modules
api_router.include_router(workspace.router, prefix="/workspaces", tags=["workspaces"])
# api_router.include_router(boards.router, prefix="/boards", tags=["boards"])
# api_router.include_router(columns.router, prefix="/columns", tags=["columns"])
# api_router.include_router(cards.router, prefix="/cards", tags=["cards"])
# api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
# api_router.include_router(attachments.router, prefix="/attachments", tags=["attachments"])
# api_router.include_router(audit.router, prefix="/audit", tags=["audit"])

# Add a placeholder endpoint for now
@api_router.get("/")
async def api_root():
    """API root endpoint."""
    return {
        "message": "Kanban For Agents API v1",
        "version": "1.0.0",
        "status": "active"
    }
