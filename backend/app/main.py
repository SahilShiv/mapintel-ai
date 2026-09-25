import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.seed_demo import seed_database
from backend.app.routers import (
    projects_router,
    competitors_router,
    posts_router,
    scraping_router,
    analysis_router,
    trends_router,
    content_ideas_router,
    generated_updates_router,
    dashboard_router,
    settings_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

from backend.app.migrate import run_migrations

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing and migrating database schema...")
    try:
        run_migrations()
    except Exception as e:
        logger.error(f"Migration error: {e}")
    logger.info("Seeding realistic demo dataset if repository is empty...")
    try:
        seed_database()
    except Exception as e:
        logger.error(f"Error checking/seeding database on startup: {e}")
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="Full-stack Competitor Update Intelligence Platform focused on Google Maps Posts."
)

# Robust environment-configured CORS
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]
if settings.FRONTEND_URL and settings.FRONTEND_URL not in allowed_origins:
    allowed_origins.append(settings.FRONTEND_URL.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(projects_router, prefix=settings.API_V1_STR)
app.include_router(competitors_router, prefix=settings.API_V1_STR)
app.include_router(posts_router, prefix=settings.API_V1_STR)
app.include_router(scraping_router, prefix=settings.API_V1_STR)
app.include_router(analysis_router, prefix=settings.API_V1_STR)
app.include_router(trends_router, prefix=settings.API_V1_STR)
app.include_router(content_ideas_router, prefix=settings.API_V1_STR)
app.include_router(generated_updates_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health")
@app.get(f"{settings.API_V1_STR}/health")
def health():
    db_status = "disconnected"
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Healthcheck database ping failed: {e}")
        db_status = f"error: {str(e)}"
    finally:
        db.close()

    return {
        "status": "ok" if db_status == "connected" else "degraded",
        "database": db_status,
        "version": settings.VERSION
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Stored repository data remains safe."}
    )
