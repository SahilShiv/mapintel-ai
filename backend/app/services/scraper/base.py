from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from abc import ABC, abstractmethod

@dataclass
class ScrapedPost:
    post_url: Optional[str] = None
    post_text: Optional[str] = None
    published_date: Optional[datetime] = None
    media_urls: List[str] = field(default_factory=list)
    call_to_action: Optional[str] = None
    source_post_id: Optional[str] = None
    detected_keywords: List[str] = field(default_factory=list)
    industry_topic: Optional[str] = None
    content_type: Optional[str] = "Update"
    raw_payload: Optional[Dict[str, Any]] = None

@dataclass
class ScrapeResult:
    competitor_id: Optional[int]
    competitor_name: str
    status: str # "success", "failed", "captcha_required"
    posts_found: int = 0
    new_posts: int = 0
    duplicates_skipped: int = 0
    images_downloaded: int = 0
    posts: List[ScrapedPost] = field(default_factory=list)
    error_message: Optional[str] = None
    log_message: Optional[str] = None
    captcha_detected: bool = False

class BaseScraper(ABC):
    @abstractmethod
    def scrape_competitor(
        self,
        competitor_id: Optional[int],
        competitor_name: str,
        google_maps_url: str,
        job_id: Optional[int] = None
    ) -> ScrapeResult:
        """Extract posts from a competitor's Google Maps profile."""
        pass
