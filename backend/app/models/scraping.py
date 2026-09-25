from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(String(50), default="live", nullable=False) # 'live' or 'demo'
    start_time = Column(DateTime, default=utc_now, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(50), default="Pending", nullable=False) 
    # Pending, Running, Completed, Completed with Errors, Failed, Manual Intervention Required
    
    competitors_processed = Column(Integer, default=0, nullable=False)
    total_competitors = Column(Integer, default=0, nullable=False)
    posts_found = Column(Integer, default=0, nullable=False)
    valid_posts = Column(Integer, default=0, nullable=False)
    new_posts = Column(Integer, default=0, nullable=False)
    duplicates_skipped = Column(Integer, default=0, nullable=False)
    images_downloaded = Column(Integer, default=0, nullable=False)
    failures = Column(Integer, default=0, nullable=False)
    captcha_detected = Column(Boolean, default=False, nullable=False)
    error_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    project = relationship("Project", back_populates="scraping_jobs")
    items = relationship("ScrapingJobItem", back_populates="job", cascade="all, delete-orphan")


class ScrapingJobItem(Base):
    __tablename__ = "scraping_job_items"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("scraping_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    competitor_id = Column(Integer, nullable=True)
    competitor_name = Column(String(255), nullable=False)
    status = Column(String(50), default="success", nullable=False) # SUCCESS, PARTIAL_SUCCESS, EXTRACTION_FAILED, CAPTCHA_REQUIRED, NETWORK_ERROR, FAILED
    posts_found = Column(Integer, default=0, nullable=False)
    valid_posts = Column(Integer, default=0, nullable=False)
    new_posts = Column(Integer, default=0, nullable=False)
    duplicates_skipped = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    log_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now, nullable=False)

    job = relationship("ScrapingJob", back_populates="items")
