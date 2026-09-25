from backend.app.routers.projects import router as projects_router
from backend.app.routers.competitors import router as competitors_router
from backend.app.routers.posts import router as posts_router
from backend.app.routers.scraping import router as scraping_router
from backend.app.routers.analysis import router as analysis_router
from backend.app.routers.trends import router as trends_router
from backend.app.routers.content_ideas import router as content_ideas_router
from backend.app.routers.generated_updates import router as generated_updates_router
from backend.app.routers.dashboard import router as dashboard_router
from backend.app.routers.settings import router as settings_router

__all__ = [
    "projects_router",
    "competitors_router",
    "posts_router",
    "scraping_router",
    "analysis_router",
    "trends_router",
    "content_ideas_router",
    "generated_updates_router",
    "dashboard_router",
    "settings_router",
]
