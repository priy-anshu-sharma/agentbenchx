"""API router for version 1."""

from fastapi import APIRouter

from app.api.v1.routes import agents, tasks, environments  # to be created

api_router = APIRouter()

# Include routers from each module
# api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
# api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
# api_router.include_router(environments.router, prefix="/environments", tags=["environments"])