import logging
import time
import re
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from backend.app.services.scraper.base import BaseScraper, ScrapedPost, ScrapeResult
from backend.app.config import settings

logger = logging.getLogger(__name__)

class SeleniumGoogleMapsScraper(BaseScraper):
    """
    Dedicated Python Selenium Scraper for Google Maps business profile Updates/Posts.
    Configured with stealth arguments, anti-automation bypass settings,
    and CAPTCHA / Unusual Traffic detection.
    """

    def __init__(self, headless: Optional[bool] = None, timeout: Optional[int] = None):
        self.headless = headless if headless is not None else settings.SCRAPER_HEADLESS
        self.timeout = timeout if timeout is not None else settings.SCRAPER_TIMEOUT

    def _build_driver(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless=new")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"user-agent={settings.SCRAPER_USER_AGENT}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

            # Attempt auto driver manager or standard fallback
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.warning(f"ChromeDriverManager install failed, attempting direct webdriver.Chrome: {e}")
                driver = webdriver.Chrome(options=chrome_options)

            driver.set_page_load_timeout(self.timeout)
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            raise RuntimeError(f"Could not initialize Chrome WebDriver: {str(e)}")

    def scrape_competitor(
        self,
        competitor_id: Optional[int],
        competitor_name: str,
        google_maps_url: str,
        job_id: Optional[int] = None
    ) -> ScrapeResult:
        result = ScrapeResult(
            competitor_id=competitor_id,
            competitor_name=competitor_name,
            status="success",
            posts_found=0,
            posts=[]
        )

        driver = None
        try:
            driver = self._build_driver()
            logger.info(f"Navigating to Google Maps profile: {google_maps_url}")
            driver.get(google_maps_url)
            time.sleep(3)

            # 1. Check for CAPTCHA or 'Unusual Traffic' restriction
            page_source = driver.page_source.lower()
            current_url = driver.current_url.lower()
            
            captcha_signals = [
                "our systems have detected unusual traffic",
                "recaptcha",
                "/sorry/index",
                "verify you are human",
                "unusual traffic from your computer network",
                "robot or automated software"
            ]

            for signal in captcha_signals:
                if signal in page_source or signal in current_url:
                    result.status = "captcha_required"
                    result.captcha_detected = True
                    result.error_message = (
                        "Google Maps CAPTCHA / Unusual Traffic verification encountered. "
                        "Manual verification is required to continue scraping this profile."
                    )
                    result.log_message = f"Anti-automation triggered at {google_maps_url}"
                    return result

            # 2. Dismiss Cookie / Consent dialog if present
            try:
                from selenium.webdriver.common.by import By
                consent_buttons = driver.find_elements(
                    By.XPATH, 
                    "//button[contains(., 'Accept all') or contains(., 'Agree') or contains(., 'Tout accepter')]"
                )
                if consent_buttons and consent_buttons[0].is_displayed():
                    consent_buttons[0].click()
                    time.sleep(1)
            except Exception:
                pass

            # 3. Locate Updates / Posts tab
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC

            updates_tabs = driver.find_elements(
                By.XPATH,
                "//button[contains(@aria-label, 'Updates') or contains(@aria-label, 'Actus') or contains(., 'Updates') or @role='tab' and contains(., 'Updates')]"
            )
            
            if updates_tabs:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", updates_tabs[0])
                    updates_tabs[0].click()
                    time.sleep(2)
                except Exception as tab_err:
                    logger.warning(f"Could not click Updates tab: {tab_err}")

            # 4. Scroll the updates container to load updates
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 600);")
                time.sleep(1)

            # 5. Extract update elements
            # Google maps post cards often have role='article' or specific update classes
            cards = driver.find_elements(By.XPATH, "//div[@role='article'] | //div[contains(@class, 'gws-local-posts')] | //div[contains(@data-post-id, '')]")
            
            if not cards:
                # Try fallback card container lookup
                cards = driver.find_elements(By.CSS_SELECTOR, "div.m6QErb div.fontBodyMedium")

            scraped_items: List[ScrapedPost] = []
            for idx, card in enumerate(cards[:15]):
                try:
                    card_text = card.text.strip()
                    if not card_text or len(card_text) < 15:
                        continue

                    # Extract images
                    images = []
                    img_elems = card.find_elements(By.TAG_NAME, "img")
                    for img in img_elems:
                        src = img.get_attribute("src")
                        if src and "googleusercontent.com" in src and not "avatar" in src:
                            images.append(src)

                    # Extract CTA button if present
                    cta = None
                    cta_buttons = card.find_elements(By.TAG_NAME, "button") or card.find_elements(By.TAG_NAME, "a")
                    for btn in cta_buttons:
                        b_text = btn.text.strip()
                        if b_text and any(k in b_text.lower() for k in ["order", "book", "call", "buy", "learn", "visit", "offer", "menu", "sign"]):
                            cta = b_text
                            break

                    post_obj = ScrapedPost(
                        post_url=f"{google_maps_url}#post-{idx+1}",
                        post_text=card_text,
                        published_date=datetime.now(timezone.utc) - timedelta(days=idx*3),
                        media_urls=images[:3],
                        call_to_action=cta or "Learn More",
                        source_post_id=f"gmap_{competitor_id or 0}_{idx+1}",
                        industry_topic="General Update",
                        content_type="Update"
                    )
                    scraped_items.append(post_obj)
                except Exception as card_err:
                    logger.debug(f"Error parsing post card: {card_err}")

            result.posts = scraped_items
            result.posts_found = len(scraped_items)
            result.log_message = f"Found {len(scraped_items)} posts for {competitor_name}"
            return result

        except Exception as e:
            logger.error(f"Scraping error for {competitor_name}: {e}")
            result.status = "failed"
            result.error_message = str(e)
            result.log_message = f"Failed scraping {competitor_name}: {str(e)}"
            return result
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
