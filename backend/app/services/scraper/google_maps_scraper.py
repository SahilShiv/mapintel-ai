"""
Production Google Maps Scraper
Executes modular, validated extraction of competitor Updates/Posts.
Rejects navigation elements, handles CAPTCHA detection, and ensures
status reflects real extraction fidelity.
"""

import time
import logging
from typing import Optional, List
from datetime import datetime, timezone

from backend.app.config import settings
from backend.app.services.scraper.base import BaseScraper, ScrapedPost, ScrapeResult
from backend.app.services.scraper.selectors import (
    CONSENT_BUTTON_XPATHS,
    UPDATES_TAB_XPATHS,
    POST_CONTAINER_XPATHS,
    POST_CONTAINER_CSS
)
from backend.app.services.scraper.captcha_detector import CaptchaDetector
from backend.app.services.scraper.post_parser import PostParser

logger = logging.getLogger(__name__)

class GoogleMapsSeleniumScraper(BaseScraper):
    """
    Dedicated Python Selenium Scraper for Google Maps business profile Updates/Posts.
    Strictly isolates post containers, uses modular selectors and validators,
    and accurately reports extraction failures.
    """

    def __init__(self, headless: Optional[bool] = None, timeout: Optional[int] = None):
        self.headless = headless if headless is not None else settings.SCRAPER_HEADLESS
        self.timeout = timeout if timeout is not None else settings.SCRAPER_TIMEOUT

    def _build_driver(self):
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

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.warning(f"ChromeDriverManager install failed, attempting direct webdriver.Chrome: {e}")
            driver = webdriver.Chrome(options=chrome_options)

        driver.set_page_load_timeout(self.timeout)
        return driver

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
            status="pending",
            posts_found=0,
            posts=[]
        )

        driver = None
        try:
            driver = self._build_driver()
            logger.info(f"Navigating to Google Maps profile: {google_maps_url}")
            driver.get(google_maps_url)
            time.sleep(3)

            # 1. Anti-automation / CAPTCHA Check
            is_captcha, captcha_reason = CaptchaDetector.detect(driver.page_source, driver.current_url)
            if is_captcha:
                result.status = "captcha_required"
                result.captcha_detected = True
                result.error_message = (
                    f"Google Maps security verification required: {captcha_reason}. "
                    "Manual verification is required to continue scraping this profile."
                )
                result.log_message = f"CAPTCHA/Unusual traffic detected at {google_maps_url}"
                return result

            # 2. Dismiss Cookie / Consent dialog if present
            from selenium.webdriver.common.by import By
            for consent_xpath in CONSENT_BUTTON_XPATHS:
                try:
                    btns = driver.find_elements(By.XPATH, consent_xpath)
                    if btns and btns[0].is_displayed():
                        btns[0].click()
                        time.sleep(1)
                        break
                except Exception:
                    pass

            # 3. Locate and switch to the Updates / Posts tab
            tab_clicked = False
            for tab_xpath in UPDATES_TAB_XPATHS:
                try:
                    tabs = driver.find_elements(By.XPATH, tab_xpath)
                    for tab in tabs:
                        if tab.is_displayed():
                            driver.execute_script("arguments[0].scrollIntoView(true);", tab)
                            tab.click()
                            tab_clicked = True
                            time.sleep(2)
                            break
                    if tab_clicked:
                        break
                except Exception as tab_err:
                    logger.debug(f"Could not click tab with xpath {tab_xpath}: {tab_err}")

            # 4. Scroll down in the updates panel to trigger dynamic post card loading
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(0.8)

            # 5. Locate Post Container Cards
            card_elements = []
            for xpath in POST_CONTAINER_XPATHS:
                try:
                    elems = driver.find_elements(By.XPATH, xpath)
                    if elems:
                        card_elements = elems
                        break
                except Exception:
                    continue

            if not card_elements:
                for css in POST_CONTAINER_CSS:
                    try:
                        elems = driver.find_elements(By.CSS_SELECTOR, css)
                        if elems:
                            card_elements = elems
                            break
                    except Exception:
                        continue

            # 6. Parse cards with strict PostContentValidator
            valid_posts: List[ScrapedPost] = []
            rejection_reasons: List[str] = []

            for idx, card in enumerate(card_elements[:15]):
                parsed_post, rejection_reason = PostParser.parse_card(
                    card_element=card,
                    competitor_name=competitor_name,
                    google_maps_url=google_maps_url,
                    index=idx
                )
                if parsed_post:
                    valid_posts.append(parsed_post)
                else:
                    rejection_reasons.append(rejection_reason or "Unknown rejection")

            # 7. Evaluate outcome - NEVER mark extraction as success if 0 valid posts found
            if not valid_posts:
                result.status = "extraction_failed"
                if not card_elements:
                    reason = "Google Maps Updates/Post container could not be identified."
                else:
                    reason = f"All {len(card_elements)} candidate elements failed post validation (e.g. {rejection_reasons[0] if rejection_reasons else 'page UI labels'})."
                result.error_message = reason
                result.log_message = f"Extraction failed for {competitor_name}: {reason}"
                result.posts_found = 0
                return result

            # Extraction Succeeded with Valid Posts
            result.status = "success"
            result.posts = valid_posts
            result.posts_found = len(valid_posts)
            result.log_message = f"Extracted {len(valid_posts)} valid Google Maps updates for {competitor_name}"
            return result

        except Exception as e:
            logger.error(f"Error scraping {competitor_name}: {e}")
            result.status = "failed"
            result.error_message = str(e)
            result.log_message = f"Scraper execution error: {str(e)}"
            return result
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
