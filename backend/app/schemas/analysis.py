from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TopicMetric(BaseModel):
    topic: str
    count: int
    percentage: float
    competitors_count: int
    competitors: List[str]

class KeywordMetric(BaseModel):
    keyword: str
    count: int
    percentage: float

class ContentTypeMetric(BaseModel):
    content_type: str
    count: int
    percentage: float

class CTAMetric(BaseModel):
    call_to_action: str
    count: int
    percentage: float

class CompetitorPostingMetric(BaseModel):
    competitor_id: int
    competitor_name: str
    post_count: int
    latest_post_date: Optional[datetime] = None
    top_topics: List[str] = []

class TimelinePoint(BaseModel):
    period: str # e.g. "2026-W38" or "2026-09"
    count: int

class TrendAnalysisResponse(BaseModel):
    project_id: int
    total_posts: int
    top_topics: List[TopicMetric]
    top_keywords: List[KeywordMetric]
    content_types: List[ContentTypeMetric]
    call_to_actions: List[CTAMetric]
    competitor_activity: List[CompetitorPostingMetric]
    posting_timeline: List[TimelinePoint]
    ai_insights: Optional[str] = None
    calculated_at: datetime

class AnalysisTriggerRequest(BaseModel):
    project_id: int
    force_reanalyze: Optional[bool] = False
    provider: Optional[str] = None # "gemini", "grok", or auto
