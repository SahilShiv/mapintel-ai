import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Google Maps Competitor Update Intelligence Tool"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database: SQLite default for instant zero-dependency local dev/eval, PostgreSQL for production
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./intelligence_tool.db")
    
    # AI Providers
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    GROK_API_KEY: Optional[str] = os.getenv("GROK_API_KEY", None)
    GROK_BASE_URL: str = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
    DEFAULT_AI_PROVIDER: str = os.getenv("DEFAULT_AI_PROVIDER", "gemini") # "gemini" or "grok"
    
    # Scraper Settings
    SCRAPER_HEADLESS: bool = os.getenv("SCRAPER_HEADLESS", "true").lower() in ("true", "1", "yes")
    SCRAPER_TIMEOUT: int = int(os.getenv("SCRAPER_TIMEOUT", "15"))
    SCRAPER_USER_AGENT: str = os.getenv(
        "SCRAPER_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
    
    # CORS
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
