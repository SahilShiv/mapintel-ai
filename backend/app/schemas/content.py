from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class ContentIdeaRequest(BaseModel):
    project_id: int
    count: int = Field(10, ge=1, le=50) # exactly 3, 5, 10, 20, 50
    focus_topic: Optional[str] = None
    provider: Optional[str] = None

class GeneratedIdeaResponse(BaseModel):
    id: int
    project_id: int
    title: str
    topic: str
    description: str
    relevant_keywords: Optional[str] = None
    suggested_cta: Optional[str] = None
    competitor_insight: Optional[str] = None
    ai_provider: str
    model_used: str
    created_at: datetime

    class Config:
        from_attributes = True

class ContentIdeaBatchResponse(BaseModel):
    project_id: int
    requested_count: int
    generated_count: int
    skipped_duplicates: int
    ideas: List[GeneratedIdeaResponse]

class GenerateUpdateRequest(BaseModel):
    project_id: int
    idea_id: Optional[int] = None
    topic: Optional[str] = None
    custom_prompt: Optional[str] = None
    provider: Optional[str] = None

class GeneratedUpdateResponse(BaseModel):
    id: int
    project_id: int
    idea_id: Optional[int] = None
    topic: str
    update_copy: str
    relevant_keywords: Optional[str] = None
    call_to_action: Optional[str] = None
    image_concept: Optional[str] = None
    generated_image_url: Optional[str] = None
    ai_provider: str
    model_used: str
    created_at: datetime

    class Config:
        from_attributes = True
