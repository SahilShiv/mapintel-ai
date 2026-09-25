from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class ScrapingTriggerRequest(BaseModel):
    project_id: int
    competitor_ids: Optional[List[int]] = None # If none, scrapes all project competitors
    mode: Optional[str] = "demo" # "live" or "demo"
    sync: Optional[bool] = False # True for synchronous execution, False for async background with polling

class ScrapingJobItemResponse(BaseModel):
    id: int
    competitor_id: Optional[int] = None
    competitor_name: str
    status: str
    posts_found: int
    valid_posts: int = 0
    new_posts: int
    duplicates_skipped: int
    error_message: Optional[str] = None
    log_message: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class ScrapingJobResponse(BaseModel):
    id: int
    project_id: int
    job_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    competitors_processed: int
    total_competitors: int
    posts_found: int
    valid_posts: int = 0
    new_posts: int
    duplicates_skipped: int
    images_downloaded: int
    failures: int
    captcha_detected: bool
    error_details: Optional[str] = None
    created_at: datetime
    items: List[ScrapingJobItemResponse] = []

    class Config:
        from_attributes = True
