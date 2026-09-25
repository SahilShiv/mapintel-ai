"""
Google Maps Post Parser
Extracts strictly isolated post text, media, CTA, and dates from individual post cards.
Never extracts whole-page body or navigation elements.
"""

import re
import logging
from typing import Optional, List, Tuple
from datetime import datetime, timezone, timedelta

from backend.app.services.scraper.base import ScrapedPost
from backend.app.services.scraper.selectors import (
    POST_TEXT_XPATHS,
    EXPAND_BUTTON_XPATHS,
    POST_DATE_XPATHS,
    POST_CTA_XPATHS,
    POST_IMAGE_XPATHS
)
from backend.app.services.scraper.validation import PostContentValidator

logger = logging.getLogger(__name__)

class PostParser:
    @staticmethod
    def parse_card(
        card_element,
        competitor_name: str,
        google_maps_url: str,
        index: int
    ) -> Tuple[Optional[ScrapedPost], Optional[str]]:
        """
        Parses a single post container element.
        Returns (ScrapedPost, None) on success, or (None, rejection_reason) on failure.
        """
        try:
            from selenium.webdriver.common.by import By

            # 1. Expand "More" / read more button if present inside this card
            for xpath in EXPAND_BUTTON_XPATHS:
                try:
                    expand_btns = card_element.find_elements(By.XPATH, xpath)
                    for b in expand_btns:
                        if b.is_displayed():
                            b.click()
                            break
                except Exception:
                    pass

            # 2. Extract strictly isolated post text
            raw_text = None
            for xpath in POST_TEXT_XPATHS:
                try:
                    elems = card_element.find_elements(By.XPATH, xpath)
                    for el in elems:
                        txt = el.text.strip()
                        if txt and len(txt) > 10:
                            raw_text = txt
                            break
                    if raw_text:
                        break
                except Exception:
                    continue

            # If specific text element wasn't isolated, extract card's own text
            if not raw_text:
                raw_text = card_element.text.strip()

            # 3. Validate extracted text with PostContentValidator
            is_valid, reason = PostContentValidator.validate(raw_text)
            if not is_valid:
                logger.debug(f"Card {index+1} for {competitor_name} failed validation: {reason}")
                return None, reason

            cleaned_text = PostContentValidator.clean_text(raw_text)

            # 4. Extract post-specific media
            images: List[str] = []
            for img_xpath in POST_IMAGE_XPATHS:
                try:
                    img_elements = card_element.find_elements(By.XPATH, img_xpath)
                    for img in img_elements:
                        src = img.get_attribute("src")
                        if PostContentValidator.is_valid_image_url(src) and src not in images:
                            images.append(src)
                except Exception:
                    continue

            # 5. Extract CTA button
            cta = None
            for cta_xpath in POST_CTA_XPATHS:
                try:
                    cta_elements = card_element.find_elements(By.XPATH, cta_xpath)
                    for el in cta_elements:
                        t = el.text.strip()
                        if t and len(t) < 40 and not any(k in t.lower() for k in ["share", "save", "directions"]):
                            cta = t
                            break
                    if cta:
                        break
                except Exception:
                    continue

            # 6. Extract published date or fallback
            parsed_date = None
            for date_xpath in POST_DATE_XPATHS:
                try:
                    date_elements = card_element.find_elements(By.XPATH, date_xpath)
                    for el in date_elements:
                        d_text = el.text.strip().lower()
                        if "ago" in d_text:
                            parsed_date = PostParser._parse_relative_date(d_text)
                            break
                    if parsed_date:
                        break
                except Exception:
                    continue

            if not parsed_date:
                parsed_date = datetime.now(timezone.utc) - timedelta(days=index * 3)

            # 7. Construct post object
            post_id_attr = card_element.get_attribute("data-post-id") or f"card_{index+1}"
            post_url = f"{google_maps_url}#post-{index+1}"

            post = ScrapedPost(
                post_url=post_url,
                post_text=cleaned_text,
                published_date=parsed_date,
                media_urls=images[:4],
                call_to_action=cta or "Learn More",
                source_post_id=f"gmap_{competitor_name.lower().replace(' ', '_')}_{post_id_attr}",
                industry_topic="General Update",
                content_type="Update"
            )
            return post, None

        except Exception as e:
            return None, f"Parsing exception: {str(e)}"

    @staticmethod
    def _parse_relative_date(text: str) -> datetime:
        now = datetime.now(timezone.utc)
        match = re.search(r'(\d+)\s*(hour|day|week|month|year)s?\s*ago', text)
        if match:
            val = int(match.group(1))
            unit = match.group(2)
            if unit == "hour":
                return now - timedelta(hours=val)
            elif unit == "day":
                return now - timedelta(days=val)
            elif unit == "week":
                return now - timedelta(weeks=val)
            elif unit == "month":
                return now - timedelta(days=val * 30)
            elif unit == "year":
                return now - timedelta(days=val * 365)
        return now
