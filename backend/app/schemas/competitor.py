from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class CompetitorBase(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    google_maps_url: str = Field(..., min_length=5)
    place_identifier: Optional[str] = None
    status: Optional[str] = "active"

class CompetitorCreate(CompetitorBase):
    pass

class CompetitorUpdate(BaseModel):
    business_name: Optional[str] = None
    google_maps_url: Optional[str] = None
    place_identifier: Optional[str] = None
    status: Optional[str] = None

class CompetitorResponse(CompetitorBase):
    id: int
    project_id: int
    last_scraped_at: Optional[datetime] = None
    total_posts: int
    scraping_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
