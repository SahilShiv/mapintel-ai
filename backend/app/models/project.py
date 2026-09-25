from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    client_business_name = Column(String(255), nullable=False)
    google_maps_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    verified_facts = Column(Text, nullable=True) # JSON string or structured text of client verified facts
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    competitors = relationship("Competitor", back_populates="project", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="project", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="project", cascade="all, delete-orphan")
    scraping_jobs = relationship("ScrapingJob", back_populates="project", cascade="all, delete-orphan")
    generated_ideas = relationship("GeneratedIdea", back_populates="project", cascade="all, delete-orphan")
    generated_updates = relationship("GeneratedUpdate", back_populates="project", cascade="all, delete-orphan")


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    business_name = Column(String(255), nullable=False)
    google_maps_url = Column(Text, nullable=False)
    place_identifier = Column(String(255), nullable=True)
    status = Column(String(50), default="active", nullable=False)
    last_scraped_at = Column(DateTime, nullable=True)
    total_posts = Column(Integer, default=0, nullable=False)
    scraping_status = Column(String(50), default="idle", nullable=False) # idle, pending, running, completed, error, captcha_required
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    project = relationship("Project", back_populates="competitors")
    posts = relationship("Post", back_populates="competitor", cascade="all, delete-orphan")


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    project = relationship("Project", back_populates="keywords")

    __table_args__ = (
        Index("idx_keyword_project", "project_id", "keyword"),
    )
