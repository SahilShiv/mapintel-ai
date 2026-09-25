from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PostAnalysisResult(BaseModel):
    main_topic: str
    sub_topic: str
    keywords: List[str]
    content_type: str
    call_to_action: str
    offer_pattern: Optional[str] = None
    sentiment: str = "positive"

class ContentIdeaResult(BaseModel):
    title: str
    topic: str
    description: str
    relevant_keywords: List[str]
    suggested_cta: str
    competitor_insight: str

class UpdateDraftResult(BaseModel):
    topic: str
    update_copy: str
    relevant_keywords: List[str]
    call_to_action: str
    image_concept: str

class AIProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def default_model(self) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider API key and configuration are active."""
        pass

    @abstractmethod
    def analyze_post(self, post_text: str, competitor_name: str) -> PostAnalysisResult:
        """Analyze a single competitor Google Maps post."""
        pass

    @abstractmethod
    def generate_content_ideas(
        self,
        client_name: str,
        project_description: str,
        competitor_posts_summary: str,
        count: int,
        existing_ideas: List[str],
        focus_topic: Optional[str] = None
    ) -> List[ContentIdeaResult]:
        """Generate high-performing Google Maps content ideas based on competitor intel."""
        pass

    @abstractmethod
    def generate_complete_update(
        self,
        client_name: str,
        business_type: str,
        topic: str,
        idea_context: Optional[str],
        competitor_insights: str,
        client_facts: Optional[str] = None
    ) -> UpdateDraftResult:
        """Generate a complete, publish-ready Google Maps update with copy, CTAs, and image direction."""
        pass
