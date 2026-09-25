from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    competitor_name = Column(String(255), nullable=False)
    
    google_maps_profile_url = Column(Text, nullable=True)
    post_url = Column(Text, nullable=True, index=True)
    post_text = Column(Text, nullable=True)
    published_date = Column(DateTime, nullable=True, index=True)
    
    call_to_action = Column(String(255), nullable=True)
    detected_keywords = Column(Text, nullable=True) # comma-separated list
    industry_topic = Column(String(255), nullable=True, index=True)
    content_type = Column(String(100), nullable=True) # Offer, Tip, Product Update, Event, Showcase
    
    source_information = Column(String(50), default="DEMO", nullable=False) # Backwards compatibility
    source_type = Column(String(50), default="DEMO", index=True, nullable=False) # LIVE, DEMO, SEEDED
    is_valid = Column(Boolean, default=True, index=True, nullable=False) # True = clean post, False = rejected UI garbage
    validation_error = Column(Text, nullable=True)

    fingerprint = Column(String(64), unique=True, index=True, nullable=False) # SHA256 hex
    scraped_at = Column(DateTime, default=utc_now, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="posts")
    competitor = relationship("Competitor", back_populates="posts")
    media = relationship("PostMedia", back_populates="post", cascade="all, delete-orphan")
    analysis = relationship("PostAnalysis", back_populates="post", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_posts_proj_comp", "project_id", "competitor_id"),
        Index("idx_posts_date", "published_date"),
        Index("idx_posts_topic", "industry_topic"),
        Index("idx_posts_valid", "is_valid"),
        Index("idx_posts_src", "source_type"),
    )


class InvalidScrapedRecord(Base):
    """
    Dedicated storage table for rejected scraping records that contained Google Maps
    page UI text, navigation dumps, or failed post content validation.
    Ensures repository analytics and AI are never polluted.
    """
    __tablename__ = "invalid_scraped_records"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    competitor_id = Column(Integer, nullable=True, index=True)
    competitor_name = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=False)
    source_type = Column(String(50), default="LIVE", nullable=False) # LIVE or DEMO
    created_at = Column(DateTime, default=utc_now, nullable=False)


class PostMedia(Base):
    __tablename__ = "post_media"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    media_type = Column(String(50), default="image", nullable=False)
    media_url = Column(Text, nullable=False)
    thumbnail_url = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    post = relationship("Post", back_populates="media")


class PostAnalysis(Base):
    __tablename__ = "post_analysis"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    main_topic = Column(String(255), nullable=True)
    sub_topic = Column(String(255), nullable=True)
    keywords = Column(Text, nullable=True) # JSON string list
    content_type = Column(String(100), nullable=True)
    call_to_action = Column(String(255), nullable=True)
    offer_pattern = Column(String(255), nullable=True)
    sentiment = Column(String(50), nullable=True)
    ai_provider = Column(String(50), nullable=True)
    analyzed_at = Column(DateTime, default=utc_now, nullable=False)

    post = relationship("Post", back_populates="analysis")
