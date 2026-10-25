"""
API router package for Student Skill Gap Analyzer.
"""
from app.routes.health import router as health_router
from app.routes.auth import router as auth_router
from app.routes.analyses import router as analyses_router
from app.routes.roadmaps import router as roadmaps_router

__all__ = [
    "health_router",
    "auth_router",
    "analyses_router",
    "roadmaps_router",
]
