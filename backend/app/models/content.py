from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class GeneratedIdea(Base):
    __tablename__ = "generated_ideas"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    relevant_keywords = Column(Text, nullable=True) # comma-separated
    suggested_cta = Column(String(255), nullable=True)
    competitor_insight = Column(Text, nullable=True)
    ai_provider = Column(String(50), default="gemini", nullable=False)
    model_used = Column(String(100), default="gemini-1.5-flash", nullable=False)
    semantic_hash = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    project = relationship("Project", back_populates="generated_ideas")


class GeneratedUpdate(Base):
    __tablename__ = "generated_updates"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    idea_id = Column(Integer, ForeignKey("generated_ideas.id", ondelete="SET NULL"), nullable=True)
    topic = Column(String(255), nullable=False)
    update_copy = Column(Text, nullable=False)
    relevant_keywords = Column(Text, nullable=True)
    call_to_action = Column(String(255), nullable=True)
    image_concept = Column(Text, nullable=True)
    generated_image_url = Column(Text, nullable=True)
    ai_provider = Column(String(50), default="gemini", nullable=False)
    model_used = Column(String(100), default="gemini-1.5-flash", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    project = relationship("Project", back_populates="generated_updates")
