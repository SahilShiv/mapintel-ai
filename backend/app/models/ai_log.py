from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class AIProviderLog(Base):
    __tablename__ = "ai_provider_logs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=True, index=True)
    provider = Column(String(50), nullable=False) # gemini, grok, fallback
    model = Column(String(100), nullable=False)
    action_type = Column(String(50), nullable=False) # analysis, idea_generation, update_generation
    status = Column(String(50), nullable=False) # success, error, fallback_invoked
    error_message = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
