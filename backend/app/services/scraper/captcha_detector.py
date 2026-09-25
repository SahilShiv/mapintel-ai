"""
Google Maps Anti-Automation & CAPTCHA Detector
Detects Google bot checkpoints, rate limits, and verification requirements.
"""

from typing import Tuple

CAPTCHA_SIGNATURES = [
    "our systems have detected unusual traffic",
    "recaptcha",
    "/sorry/index",
    "/sorry/",
    "verify you are human",
    "unusual traffic from your computer network",
    "robot or automated software",
    "please solve this challenge",
    "security check to continue"
]

class CaptchaDetector:
    @staticmethod
    def detect(page_source: str, current_url: str) -> Tuple[bool, str]:
        """
        Inspects page content and URL to detect anti-automation triggers.
        Returns (is_captcha, reason).
        """
        src_lower = (page_source or "").lower()
        url_lower = (current_url or "").lower()

        if "/sorry/" in url_lower:
            return True, "Google Maps redirected to /sorry/ verification challenge"

        for sig in CAPTCHA_SIGNATURES:
            if sig in src_lower or sig in url_lower:
                return True, f"Google Maps anti-automation trigger detected: '{sig}'"

        return False, ""
