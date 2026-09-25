import hashlib
import re
from typing import Optional
from datetime import datetime

def normalize_text(text: Optional[str]) -> str:
    """Normalize text by lowercasing, removing extra whitespace, and stripping special symbols."""
    if not text:
        return ""
    # Strip whitespace, lowercase
    cleaned = text.strip().lower()
    # Replace multiple whitespace/newlines with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    # Remove excessive punctuation
    cleaned = re.sub(r'[\r\n\t]+', ' ', cleaned)
    return cleaned

def generate_post_fingerprint(
    post_url: Optional[str] = None,
    source_post_id: Optional[str] = None,
    competitor_name: Optional[str] = None,
    post_text: Optional[str] = None,
    published_date: Optional[datetime] = None,
    profile_url: Optional[str] = None,
) -> str:
    """
    Robust fingerprint generation with strict priority:
    1. Direct post URL (if valid Google Maps post URL with specific query/data)
    2. Explicit source/post ID
    3. Stable combination of competitor + normalized post text + published date + profile URL
    """
    if post_url and len(post_url.strip()) > 15 and ("google.com" in post_url or "goo.gl" in post_url):
        # Clean tracking params if any
        normalized_url = post_url.split("&ved=")[0].split("?ved=")[0].strip().lower()
        return hashlib.sha256(f"url::{normalized_url}".encode("utf-8")).hexdigest()

    if source_post_id and len(source_post_id.strip()) > 0:
        return hashlib.sha256(f"id::{source_post_id.strip().lower()}".encode("utf-8")).hexdigest()

    # Stable combination
    norm_comp = normalize_text(competitor_name)
    norm_text = normalize_text(post_text)
    # Take first 150 chars of normalized text to avoid tiny whitespace drift
    snippet = norm_text[:180]
    date_str = published_date.strftime("%Y-%m-%d") if published_date else "nodate"
    norm_profile = normalize_text(profile_url)

    composite = f"comp:{norm_comp}|date:{date_str}|snip:{snippet}|prof:{norm_profile}"
    return hashlib.sha256(composite.encode("utf-8")).hexdigest()


def generate_idea_semantic_hash(title: str, topic: str, description: str) -> str:
    """
    Generate normalized hash to prevent repeating generated ideas for the same project.
    """
    norm_topic = normalize_text(topic)
    norm_title = normalize_text(title)
    # Extract significant keywords (alphanumeric words > 3 chars)
    words = sorted(list(set(re.findall(r'\b[a-z]{4,}\b', normalize_text(description)))))
    key_terms = "-".join(words[:8])
    composite = f"{norm_topic}::{norm_title}::{key_terms}"
    return hashlib.sha256(composite.encode("utf-8")).hexdigest()
