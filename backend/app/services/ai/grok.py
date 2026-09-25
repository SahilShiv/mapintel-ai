import json
import logging
import re
from typing import List, Optional
from openai import OpenAI
from backend.app.config import settings
from backend.app.services.ai.base import (
    AIProvider,
    PostAnalysisResult,
    ContentIdeaResult,
    UpdateDraftResult
)

logger = logging.getLogger(__name__)

class GrokProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.GROK_API_KEY
        self.base_url = base_url or settings.GROK_BASE_URL
        self._client = None
        if self.api_key:
            try:
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except Exception as e:
                logger.warning(f"Could not initialize Grok/OpenAI client: {e}")

    @property
    def provider_name(self) -> str:
        return "grok"

    @property
    def default_model(self) -> str:
        return "grok-beta"

    def is_available(self) -> bool:
        return bool(self.api_key and self._client)

    def _extract_json(self, text: str) -> dict:
        cleaned = re.sub(r'```json\s*', '', text)
        cleaned = re.sub(r'```\s*$', '', cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            match = re.search(r'(\{.*\}|\[.*\])', cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Could not parse JSON from model output: {text[:200]}")

    def analyze_post(self, post_text: str, competitor_name: str) -> PostAnalysisResult:
        if not self.is_available():
            raise RuntimeError("Grok API key is not configured.")

        messages = [
            {"role": "system", "content": "You are a Google Maps competitor intelligence analyst. Return ONLY valid JSON."},
            {"role": "user", "content": f"""Analyze this competitor Google Maps update from "{competitor_name}":
"{post_text}"

Schema:
{{
  "main_topic": "string",
  "sub_topic": "string",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "content_type": "string (Offer, Tip, Product Update, Event, Showcase)",
  "call_to_action": "string",
  "offer_pattern": "string or null",
  "sentiment": "positive or neutral"
}}"""}
        ]

        response = self._client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            response_format={"type": "json_object"} if "openai.com" in self.base_url else None,
            temperature=0.3
        )
        content = response.choices[0].message.content
        data = self._extract_json(content)
        return PostAnalysisResult(
            main_topic=data.get("main_topic", "General Update"),
            sub_topic=data.get("sub_topic", "Notice"),
            keywords=data.get("keywords", ["google maps"]),
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
            raise RuntimeError("Grok API key is not configured.")

        prompt = f"""
Strategist for "{client_name}". Context: {project_description}.
Competitor research:
{competitor_posts_summary}

Avoid repeating these existing ideas:
{json.dumps(existing_ideas[:25])}

Generate EXACTLY {count} distinct Google Maps update ideas.
{f'Focus on topic: {focus_topic}' if focus_topic else ''}

Return JSON with format:
{{
  "ideas": [
    {{
      "title": "...",
      "topic": "...",
      "description": "...",
      "relevant_keywords": ["..."],
      "suggested_cta": "...",
      "competitor_insight": "..."
    }}
  ]
}}
"""
        response = self._client.chat.completions.create(
            model=self.default_model,
            messages=[
                {"role": "system", "content": "You are an expert Google Business Profile growth strategist. Return JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content
        data = self._extract_json(content)
        ideas_raw = data.get("ideas", data if isinstance(data, list) else [])

        results = []
        for item in ideas_raw[:count]:
            results.append(ContentIdeaResult(
                title=item.get("title", "Post Idea"),
                topic=item.get("topic", focus_topic or "General"),
                description=item.get("description", ""),
                relevant_keywords=item.get("relevant_keywords", []),
                suggested_cta=item.get("suggested_cta", "Book Now"),
                competitor_insight=item.get("competitor_insight", "Engineered to outperform competitor posting cadence.")
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
            raise RuntimeError("Grok API key is not configured.")

        facts_instruction = (
            f"VERIFIED CLIENT BUSINESS FACTS:\n{client_facts}\n"
            "CRITICAL INTEGRITY RULE: You may ONLY mention business claims, services, guarantees, years of experience, or certifications "
            "that are explicitly stated in the Verified Client Business Facts above. DO NOT invent unverified claims. If details are not provided, "
            "use neutral, professional phrasing."
            if client_facts and client_facts.strip()
            else "CRITICAL INTEGRITY RULE: No specific client facts provided. Use neutral, professional phrasing. NEVER invent specific discounts, years of experience, facility claims, or certifications."
        )

        prompt = f"""
Draft a complete Google Maps Business Update for:
Client: "{client_name}" ({business_type})
Topic: "{topic}"
Context: "{idea_context}"

{facts_instruction}

Competitor benchmark: {competitor_insights}

Return JSON:
{{
  "topic": "{topic}",
  "update_copy": "Complete copy (100-200 words with localized value proposition)",
  "relevant_keywords": ["keyword1", "keyword2"],
  "call_to_action": "CTA text",
  "image_concept": "Creative visual description"
}}
"""
        response = self._client.chat.completions.create(
            model=self.default_model,
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        data = self._extract_json(response.choices[0].message.content)
        return UpdateDraftResult(
            topic=data.get("topic", topic),
            update_copy=data.get("update_copy", ""),
            relevant_keywords=data.get("relevant_keywords", []),
            call_to_action=data.get("call_to_action", "Learn More"),
            image_concept=data.get("image_concept", "Engaging visual showcase")
        )
