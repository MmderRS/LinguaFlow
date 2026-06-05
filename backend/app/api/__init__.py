from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.history import router as history_router
from app.api.settings import router as settings_router
from app.api.terms import router as terms_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/api", tags=["health"])
api_router.include_router(settings_router, prefix="/api", tags=["settings"])
api_router.include_router(terms_router, prefix="/api", tags=["terms"])
api_router.include_router(history_router, prefix="/api", tags=["history"])
