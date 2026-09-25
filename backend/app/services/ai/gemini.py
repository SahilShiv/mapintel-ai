import json
import logging
import re
from typing import List, Optional
from backend.app.config import settings
from backend.app.services.ai.base import (
    AIProvider,
    PostAnalysisResult,
    ContentIdeaResult,
    UpdateDraftResult
)

logger = logging.getLogger(__name__)

class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize google.genai Client: {e}")

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return "gemini-2.5-flash"

    def is_available(self) -> bool:
        return bool(self.api_key and self._client)

    def _extract_json(self, text: str) -> dict:
        """Extract JSON block from markdown wrapped LLM output."""
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*$', '', cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            # Match bracketed json
            match = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Could not parse JSON from model output: {text[:200]}")

    def analyze_post(self, post_text: str, competitor_name: str) -> PostAnalysisResult:
        if not self.is_available():
            raise RuntimeError("Gemini API key is not configured.")

        prompt = f"""
You are an expert Google Maps Local SEO and competitor intelligence analyst.
Analyze the following Google Maps business update from competitor "{competitor_name}".

Post text:
"{post_text}"

Return a valid JSON object with the following schema:
{{
  "main_topic": "string (e.g. Hair Care Tips, Festival Offer, Before/After, Happy Hours, Teeth Whitening)",
  "sub_topic": "string",
  "keywords": ["list", "of", "4-6", "local", "keywords"],
  "content_type": "string (Offer, Tip, Product Update, Event, Showcase, Behind-the-scenes)",
  "call_to_action": "string (e.g. Book Now, Call Now, Order Online, Learn More)",
  "offer_pattern": "string or null (e.g. '30% Discount', '1-for-1', 'Free Consultation')",
  "sentiment": "positive or neutral"
}}
Return ONLY JSON.
"""
        response = self._client.models.generate_content(
            model=self.default_model,
            contents=prompt
        )
        data = self._extract_json(response.text)
        return PostAnalysisResult(
            main_topic=data.get("main_topic", "General Update"),
            sub_topic=data.get("sub_topic", "Business Notice"),
            keywords=data.get("keywords", ["google maps update"]),
            content_type=data.get("content_type", "Update"),
            call_to_action=data.get("call_to_action", "Learn More"),
            offer_pattern=data.get("offer_pattern"),
            sentiment=data.get("sentiment", "positive")
        )

    def generate_content_ideas(
        self,
        client_name: str,
        project_description: str,
        competitor_posts_summary: str,
        count: int,
        existing_ideas: List[str],
        focus_topic: Optional[str] = None
    ) -> List[ContentIdeaResult]:
        if not self.is_available():
            raise RuntimeError("Gemini API key is not configured.")

        prompt = f"""
You are a senior Local SEO & Google Business Profile strategist for "{client_name}".
Business Context: {project_description}

Here is intelligence gathered from top local competitors' Google Maps updates:
{competitor_posts_summary}

DO NOT duplicate or repeat the following previously generated ideas:
{json.dumps(existing_ideas[:30])}

Generate EXACTLY {count} distinct, high-converting Google Maps post ideas that will outperform competitors.
{f'Focus particularly on the topic: {focus_topic}' if focus_topic else ''}

Return ONLY a JSON array with exactly {count} objects matching this schema:
[
  {{
    "title": "Short compelling idea title",
    "topic": "Category topic",
    "description": "2-3 sentences explaining the post concept",
    "relevant_keywords": ["keyword1", "keyword2", "keyword3"],
    "suggested_cta": "Action button text (e.g. Book Now, Call Today, Claim Offer)",
    "competitor_insight": "Why this beats competitor posts based on our research"
  }}
]
"""
        response = self._client.models.generate_content(
            model=self.default_model,
            contents=prompt
        )
        raw_list = self._extract_json(response.text)
        if isinstance(raw_list, dict) and "ideas" in raw_list:
            raw_list = raw_list["ideas"]

        results = []
        for item in raw_list[:count]:
            results.append(ContentIdeaResult(
                title=item.get("title", "Local Update Idea"),
                topic=item.get("topic", focus_topic or "Local Spotlight"),
                description=item.get("description", ""),
                relevant_keywords=item.get("relevant_keywords", []),
                suggested_cta=item.get("suggested_cta", "Learn More"),
                competitor_insight=item.get("competitor_insight", "Derived from competitor topic trends.")
            ))
        return results

    def generate_complete_update(
        self,
        client_name: str,
        business_type: str,
        topic: str,
        idea_context: Optional[str],
        competitor_insights: str,
        client_facts: Optional[str] = None
    ) -> UpdateDraftResult:
        if not self.is_available():
            raise RuntimeError("Gemini API key is not configured.")

        facts_instruction = (
            f"VERIFIED CLIENT BUSINESS FACTS:\n{client_facts}\n"
            "CRITICAL INTEGRITY RULE: You may ONLY mention business facts, services, guarantees, years of experience, or certifications "
            "that are explicitly stated in the Verified Client Business Facts above. DO NOT invent claims (e.g. do NOT say '100% ammonia-free' or '10+ years experience' "
            "unless explicitly given). If information is missing, use neutral, professional phrasing like 'our dedicated team provides personalized service'."
            if client_facts and client_facts.strip()
            else "CRITICAL INTEGRITY RULE: No specific client facts provided. Use neutral, professional phrasing. NEVER invent specific discounts, years of experience, facility claims, or certifications."
        )

        prompt = f"""
You are crafting a COMPLETE, PUBLISH-READY Google Maps business update for:
Client: "{client_name}" ({business_type})
Topic: "{topic}"
Context / Concept: "{idea_context or topic}"

{facts_instruction}

Competitor Intel Benchmark:
{competitor_insights}

Create a complete Google Maps post. It should be engaging, localized, include formatting, hashtags, a clear call-to-action, and an exact art direction concept for the image.

Return ONLY a JSON object with this schema:
{{
  "topic": "{topic}",
  "update_copy": "The complete publish-ready Google Maps update post text (100-250 words with emojis and clear value hook)",
  "relevant_keywords": ["keyword1", "keyword2", "local area keyword"],
  "call_to_action": "Button text (e.g. Book Appointment, Call Now, Order Online)",
  "image_concept": "Detailed description of the ideal photo/graphic to accompany this post"
}}
"""
        response = self._client.models.generate_content(
            model=self.default_model,
            contents=prompt
        )
        data = self._extract_json(response.text)
        return UpdateDraftResult(
            topic=data.get("topic", topic),
            update_copy=data.get("update_copy", ""),
            relevant_keywords=data.get("relevant_keywords", []),
            call_to_action=data.get("call_to_action", "Book Now"),
            image_concept=data.get("image_concept", "High-quality professional business photo")
        )
