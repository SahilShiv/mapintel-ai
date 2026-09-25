import time
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.ai_log import AIProviderLog
from backend.app.services.ai.base import (
    AIProvider,
    PostAnalysisResult,
    ContentIdeaResult,
    UpdateDraftResult
)
from backend.app.services.ai.gemini import GeminiProvider
from backend.app.services.ai.grok import GrokProvider
from backend.app.services.ai.fallback import FallbackNLPProvider

logger = logging.getLogger(__name__)

class AIFactory:
    def __init__(self):
        self._gemini = GeminiProvider()
        self._grok = GrokProvider()
        self._fallback = FallbackNLPProvider()

    def get_provider(self, requested: Optional[str] = None) -> AIProvider:
        """Select requested provider if available, or fall back to an active provider."""
        req = (requested or settings.DEFAULT_AI_PROVIDER).lower()

        if req == "gemini" and self._gemini.is_available():
            return self._gemini
        elif req == "grok" and self._grok.is_available():
            return self._grok
        
        # If requested was unavailable, try the other
        if self._gemini.is_available():
            return self._gemini
        if self._grok.is_available():
            return self._grok
        
        # Robust NLP heuristic provider fallback
        return self._fallback

    def get_providers_status(self) -> Dict[str, Any]:
        """Returns availability and model info for settings & status indicators."""
        return {
            "gemini": {
                "name": "Google Gemini",
                "configured": bool(settings.GEMINI_API_KEY),
                "active": self._gemini.is_available(),
                "model": self._gemini.default_model
            },
            "grok": {
                "name": "xAI Grok",
                "configured": bool(settings.GROK_API_KEY),
                "active": self._grok.is_available(),
                "model": self._grok.default_model
            },
            "fallback_nlp": {
                "name": "Local Heuristic NLP Engine",
                "configured": True,
                "active": True,
                "model": self._fallback.default_model
            },
            "default_provider": settings.DEFAULT_AI_PROVIDER
        }

    def analyze_post_with_fallback(
        self,
        post_text: str,
        competitor_name: str,
        preferred_provider: Optional[str] = None,
        db: Optional[Session] = None,
        project_id: Optional[int] = None
    ) -> PostAnalysisResult:
        primary = self.get_provider(preferred_provider)
        start_t = time.time()

        try:
            res = primary.analyze_post(post_text, competitor_name)
            self._log(db, project_id, primary.provider_name, primary.default_model, "analysis", "success", None, start_t)
            return res
        except Exception as e:
            logger.warning(f"Provider {primary.provider_name} failed: {e}. Falling back to NLP engine.")
            self._log(db, project_id, primary.provider_name, primary.default_model, "analysis", "fallback_invoked", str(e), start_t)
            
            fb_res = self._fallback.analyze_post(post_text, competitor_name)
            self._log(db, project_id, "fallback_nlp", self._fallback.default_model, "analysis", "success", None, start_t)
            return fb_res

    def generate_ideas_with_fallback(
        self,
        client_name: str,
        project_description: str,
        competitor_summary: str,
        count: int,
        existing_ideas: List[str],
        focus_topic: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        db: Optional[Session] = None,
        project_id: Optional[int] = None
    ) -> List[ContentIdeaResult]:
        primary = self.get_provider(preferred_provider)
        start_t = time.time()

        try:
            res = primary.generate_content_ideas(
                client_name=client_name,
                project_description=project_description,
                competitor_posts_summary=competitor_summary,
                count=count,
                existing_ideas=existing_ideas,
                focus_topic=focus_topic
            )
            self._log(db, project_id, primary.provider_name, primary.default_model, "idea_generation", "success", None, start_t)
            return res
        except Exception as e:
            logger.warning(f"Provider {primary.provider_name} failed: {e}. Falling back to NLP engine.")
            self._log(db, project_id, primary.provider_name, primary.default_model, "idea_generation", "fallback_invoked", str(e), start_t)
            
            fb_res = self._fallback.generate_content_ideas(
                client_name=client_name,
                project_description=project_description,
                competitor_posts_summary=competitor_summary,
                count=count,
                existing_ideas=existing_ideas,
                focus_topic=focus_topic
            )
            self._log(db, project_id, "fallback_nlp", self._fallback.default_model, "idea_generation", "success", None, start_t)
            return fb_res

    def generate_update_with_fallback(
        self,
        client_name: str,
        business_type: str,
        topic: str,
        idea_context: Optional[str],
        competitor_insights: str,
        client_facts: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        db: Optional[Session] = None,
        project_id: Optional[int] = None
    ) -> UpdateDraftResult:
        primary = self.get_provider(preferred_provider)
        start_t = time.time()

        try:
            res = primary.generate_complete_update(
                client_name=client_name,
                business_type=business_type,
                topic=topic,
                idea_context=idea_context,
                competitor_insights=competitor_insights,
                client_facts=client_facts
            )
            self._log(db, project_id, primary.provider_name, primary.default_model, "update_generation", "success", None, start_t)
            return res
        except Exception as e:
            logger.warning(f"Provider {primary.provider_name} failed: {e}. Falling back to NLP engine.")
            self._log(db, project_id, primary.provider_name, primary.default_model, "update_generation", "fallback_invoked", str(e), start_t)
            
            fb_res = self._fallback.generate_complete_update(
                client_name=client_name,
                business_type=business_type,
                topic=topic,
                idea_context=idea_context,
                competitor_insights=competitor_insights,
                client_facts=client_facts
            )
            self._log(db, project_id, "fallback_nlp", self._fallback.default_model, "update_generation", "success", None, start_t)
            return fb_res

    def _log(self, db: Optional[Session], project_id: Optional[int], provider: str, model: str, action: str, status: str, error: Optional[str], start_t: float):
        if not db:
            return
        try:
            duration_ms = int((time.time() - start_t) * 1000)
            log = AIProviderLog(
                project_id=project_id,
                provider=provider,
                model=model,
                action_type=action,
                status=status,
                error_message=error,
                duration_ms=duration_ms
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.debug(f"Could not persist AI log: {e}")

ai_factory = AIFactory()
