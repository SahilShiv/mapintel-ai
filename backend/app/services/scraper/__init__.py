from backend.app.services.scraper.base import BaseScraper, ScrapedPost, ScrapeResult
from backend.app.services.scraper.google_maps_scraper import GoogleMapsSeleniumScraper
from backend.app.services.scraper.demo_scraper import DemoGoogleMapsScraper
from backend.app.services.scraper.validation import PostContentValidator
from backend.app.services.scraper.captcha_detector import CaptchaDetector
from backend.app.services.scraper.post_parser import PostParser
from backend.app.services.scraper.duplicate_detector import DuplicateDetector

# Backwards compatibility alias
SeleniumGoogleMapsScraper = GoogleMapsSeleniumScraper

__all__ = [
    "BaseScraper",
    "ScrapedPost",
    "ScrapeResult",
    "GoogleMapsSeleniumScraper",
    "SeleniumGoogleMapsScraper",
    "DemoGoogleMapsScraper",
    "PostContentValidator",
    "CaptchaDetector",
    "PostParser",
    "DuplicateDetector",
]
