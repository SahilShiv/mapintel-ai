from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from backend.app.schemas.competitor import CompetitorResponse
from backend.app.schemas.keyword import KeywordResponse

class ProjectBase(BaseModel):
    project_name: str = Field(..., min_length=1, max_length=255)
    client_business_name: str = Field(..., min_length=1, max_length=255)
    google_maps_url: Optional[str] = None
    description: Optional[str] = None
    verified_facts: Optional[str] = None

class ProjectCreate(ProjectBase):
    keywords: Optional[List[str]] = []

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    client_business_name: Optional[str] = None
    google_maps_url: Optional[str] = None
    description: Optional[str] = None
    verified_facts: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    competitors_count: Optional[int] = 0
    keywords_count: Optional[int] = 0
    posts_count: Optional[int] = 0
    last_scraped_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectDetailResponse(ProjectResponse):
    competitors: List[CompetitorResponse] = []
    keywords: List[KeywordResponse] = []

    class Config:
        from_attributes = True
