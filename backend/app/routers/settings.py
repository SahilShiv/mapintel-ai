from fastapi import APIRouter
from backend.app.services.ai.factory import ai_factory
from backend.app.config import settings

router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/ai-providers")
def get_ai_providers_status():
    """Returns status and configuration of AI providers without exposing API keys."""
    return ai_factory.get_providers_status()

@router.get("/system-info")
def get_system_info():
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_type": "sqlite" if settings.DATABASE_URL.startswith("sqlite") else "postgresql",
        "headless_scraping": settings.SCRAPER_HEADLESS,
        "scraper_timeout": settings.SCRAPER_TIMEOUT,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "grok_configured": bool(settings.GROK_API_KEY)
    }
