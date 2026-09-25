from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class PostMediaResponse(BaseModel):
    id: int
    media_type: str
    media_url: str
    thumbnail_url: Optional[str] = None
    caption: Optional[str] = None

    class Config:
        from_attributes = True

class PostAnalysisResponse(BaseModel):
    id: int
    main_topic: Optional[str] = None
    sub_topic: Optional[str] = None
    keywords: Optional[str] = None
    content_type: Optional[str] = None
    call_to_action: Optional[str] = None
    offer_pattern: Optional[str] = None
    sentiment: Optional[str] = None
    ai_provider: Optional[str] = None
    analyzed_at: datetime

    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: int
    project_id: int
    competitor_id: int
    competitor_name: str
    google_maps_profile_url: Optional[str] = None
    post_url: Optional[str] = None
    post_text: Optional[str] = None
    published_date: Optional[datetime] = None
    call_to_action: Optional[str] = None
    detected_keywords: Optional[str] = None
    industry_topic: Optional[str] = None
    content_type: Optional[str] = None
    source_information: str
    source_type: str = "DEMO"
    is_valid: bool = True
    validation_error: Optional[str] = None
    fingerprint: str
    scraped_at: datetime
    created_at: datetime
    media: List[PostMediaResponse] = []
    analysis: Optional[PostAnalysisResponse] = None

    class Config:
        from_attributes = True

class PostListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[PostResponse]
