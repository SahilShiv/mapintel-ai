import re
from typing import Tuple, Optional, List
from backend.app.services.scraper.selectors import UI_KEYWORD_BLACKLIST

class PostContentValidator:
    """
    Validates scraped text to guarantee that Google Maps page UI text,
    navigation labels, and whole-page body.innerText dumps NEVER become
    competitor post text in the intelligence repository.
    """

    MIN_TEXT_LENGTH = 15
    MAX_TEXT_LENGTH = 3500

    WHOLE_PAGE_SIGNATURES = [
        "send product feedback",
        "keyboard shortcuts",
        "map data ©",
        "terms of service",
        "report a problem",
        "about this data",
        "google maps sign in",
        "collapse side panel",
        "expand side panel",
        "street view & 360°"
    ]

    @classmethod
    def clean_text(cls, text: Optional[str]) -> str:
        if not text:
            return ""
        # Remove repeated whitespace and normalize newlines
        cleaned = re.sub(r'[ \t]+', ' ', text)
        cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)
        return cleaned.strip()

    @classmethod
    def validate(cls, text: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_valid, rejection_reason).
        """
        if not text or not text.strip():
            return False, "Post text is empty or contains only whitespace"

        cleaned = cls.clean_text(text)
        text_lower = cleaned.lower()

        # 1. Length boundaries
        if len(cleaned) < cls.MIN_TEXT_LENGTH:
            return False, f"Post text too short ({len(cleaned)} chars, minimum {cls.MIN_TEXT_LENGTH})"

        if len(cleaned) > cls.MAX_TEXT_LENGTH:
            return False, f"Post text length suspiciously large ({len(cleaned)} chars, maximum {cls.MAX_TEXT_LENGTH}), indicates whole-page text extraction"

        # 2. Page-wide footer / maps UI signatures
        for sig in cls.WHOLE_PAGE_SIGNATURES:
            if sig in text_lower:
                return False, f"Contains page-wide Google Maps UI footer signature: '{sig}'"

        # 3. Detect UI keyword clustering (Directions, Restaurants, Hotels, Transit, etc.)
        matched_ui_terms: List[str] = []
        for kw in UI_KEYWORD_BLACKLIST:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text_lower):
                matched_ui_terms.append(kw)

        # If 3 or more distinctive Google Maps navigation items are clustered in the text, it's UI garbage
        if len(matched_ui_terms) >= 3:
            return False, f"Contains multiple Google Maps navigation/UI keywords: {matched_ui_terms[:5]}"

        # Check UI keyword density against total word count
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text_lower)
        if words:
            ui_word_hits = sum(1 for w in words if w in UI_KEYWORD_BLACKLIST)
            density = ui_word_hits / len(words)
            if density > 0.12 and len(matched_ui_terms) >= 2:
                return False, f"Excessive Google Maps UI keyword density ({round(density*100, 1)}% of content)"

        # 4. Check for typical single UI button text dumps (e.g. text is just "Directions" or "Share")
        if text_lower in UI_KEYWORD_BLACKLIST:
            return False, f"Text is exactly a Google Maps UI label: '{text_lower}'"

        return True, None

    @classmethod
    def is_valid_image_url(cls, url: Optional[str]) -> bool:
        if not url or not isinstance(url, str):
            return False
        u = url.lower()
        if not (u.startswith("http://") or u.startswith("https://")):
            return False
        # Reject UI icons and avatars
        if "avatar" in u or "icon" in u or "sprite" in u or "cleardot.gif" in u:
            return False
        return True
