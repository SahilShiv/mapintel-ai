from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class KeywordBase(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=255)

class KeywordCreate(KeywordBase):
    pass

class KeywordResponse(KeywordBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True
