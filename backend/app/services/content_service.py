import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.app.models.project import Project
from backend.app.models.post import Post
from backend.app.models.content import GeneratedIdea, GeneratedUpdate
from backend.app.services.ai.factory import ai_factory
from backend.app.services.fingerprint import generate_idea_semantic_hash
from backend.app.schemas.content import (
    ContentIdeaRequest,
    ContentIdeaBatchResponse,
    GeneratedIdeaResponse,
    GenerateUpdateRequest,
    GeneratedUpdateResponse
)

class ContentService:
    @staticmethod
    def generate_content_ideas(
        req: ContentIdeaRequest,
        db: Session
    ) -> ContentIdeaBatchResponse:
        project = db.query(Project).filter(Project.id == req.project_id).first()
        if not project:
            raise ValueError(f"Project {req.project_id} not found")

        # 1. Gather competitor repository intelligence for context
        competitor_posts = db.query(Post).filter(Post.project_id == req.project_id).limit(20).all()
        post_snippets = [
            f"- [{p.competitor_name}] ({p.industry_topic}): {p.post_text[:140]}..."
            for p in competitor_posts if p.post_text
        ]
        competitor_summary = "\n".join(post_snippets) if post_snippets else "No competitor posts collected yet."

        # 2. Fetch existing generated ideas to enforce duplicate prevention
        existing_ideas_records = db.query(GeneratedIdea).filter(GeneratedIdea.project_id == req.project_id).all()
        existing_hashes = {i.semantic_hash for i in existing_ideas_records}
        existing_titles = [i.title for i in existing_ideas_records]

        # 3. Call AI provider for ideas
        provider_name = req.provider or "auto"
        raw_ideas = ai_factory.generate_ideas_with_fallback(
            client_name=project.client_business_name,
            project_description=project.description or f"Local business: {project.client_business_name}",
            competitor_summary=competitor_summary,
            count=req.count,
            existing_ideas=existing_titles,
            focus_topic=req.focus_topic,
            preferred_provider=provider_name,
            db=db,
            project_id=project.id
        )

        saved_ideas: List[GeneratedIdea] = []
        skipped_duplicates = 0

        for idea in raw_ideas:
            shash = generate_idea_semantic_hash(idea.title, idea.topic, idea.description)
            
            # Duplicate prevention check
            if shash in existing_hashes:
                skipped_duplicates += 1
                continue

            existing_hashes.add(shash)

            # Store persistently into database
            provider_inst = ai_factory.get_provider(req.provider)
            new_record = GeneratedIdea(
                project_id=project.id,
                title=idea.title,
                topic=idea.topic,
                description=idea.description,
                relevant_keywords=",".join(idea.relevant_keywords) if isinstance(idea.relevant_keywords, list) else idea.relevant_keywords,
                suggested_cta=idea.suggested_cta,
                competitor_insight=idea.competitor_insight,
                ai_provider=provider_inst.provider_name,
                model_used=provider_inst.default_model,
                semantic_hash=shash,
                created_at=datetime.now(timezone.utc)
            )
            db.add(new_record)
            saved_ideas.append(new_record)

            if len(saved_ideas) >= req.count:
                break

        # If duplicates were skipped and we haven't reached requested count, fetch more
        attempts = 0
        while len(saved_ideas) < req.count and attempts < 2:
            attempts += 1
            needed = req.count - len(saved_ideas)
            more_ideas = ai_factory.generate_ideas_with_fallback(
                client_name=project.client_business_name,
                project_description=project.description or f"Local business: {project.client_business_name}",
                competitor_summary=competitor_summary,
                count=needed + 3,
                existing_ideas=list(existing_titles) + [i.title for i in saved_ideas],
                focus_topic=req.focus_topic,
                preferred_provider=provider_name,
                db=db,
                project_id=project.id
            )
            for idea in more_ideas:
                shash = generate_idea_semantic_hash(idea.title, idea.topic, idea.description)
                if shash in existing_hashes:
                    skipped_duplicates += 1
                    continue
                existing_hashes.add(shash)
                provider_inst = ai_factory.get_provider(req.provider)
                new_record = GeneratedIdea(
                    project_id=project.id,
                    title=idea.title,
                    topic=idea.topic,
                    description=idea.description,
                    relevant_keywords=",".join(idea.relevant_keywords) if isinstance(idea.relevant_keywords, list) else idea.relevant_keywords,
                    suggested_cta=idea.suggested_cta,
                    competitor_insight=idea.competitor_insight,
                    ai_provider=provider_inst.provider_name,
                    model_used=provider_inst.default_model,
                    semantic_hash=shash,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(new_record)
                saved_ideas.append(new_record)
                if len(saved_ideas) >= req.count:
                    break

        db.commit()

        # Refresh all persisted items
        for item in saved_ideas:
            db.refresh(item)

        return ContentIdeaBatchResponse(
            project_id=project.id,
            requested_count=req.count,
            generated_count=len(saved_ideas),
            skipped_duplicates=skipped_duplicates,
            ideas=[GeneratedIdeaResponse.model_validate(i) for i in saved_ideas]
        )

    @staticmethod
    def generate_complete_update(
        req: GenerateUpdateRequest,
        db: Session
    ) -> GeneratedUpdateResponse:
        project = db.query(Project).filter(Project.id == req.project_id).first()
        if not project:
            raise ValueError(f"Project {req.project_id} not found")

        idea = None
        idea_context = req.custom_prompt
        topic = req.topic or "Special Announcement"

        if req.idea_id:
            idea = db.query(GeneratedIdea).filter(GeneratedIdea.id == req.idea_id).first()
            if idea:
                topic = idea.topic
                idea_context = f"Title: {idea.title}. Description: {idea.description}. Insight: {idea.competitor_insight}"

        # Get competitor insights sample from valid posts
        competitor_posts = db.query(Post).filter(Post.project_id == req.project_id, Post.is_valid == True).limit(5).all()
        comp_summary = "\n".join([f"- {p.competitor_name}: {p.post_text[:120]}" for p in competitor_posts])

        provider_inst = ai_factory.get_provider(req.provider)
        draft = ai_factory.generate_update_with_fallback(
            client_name=project.client_business_name,
            business_type="Local Business",
            topic=topic,
            idea_context=idea_context,
            competitor_insights=comp_summary,
            client_facts=project.verified_facts,
            preferred_provider=req.provider,
            db=db,
            project_id=project.id
        )

        # Store generated update in database
        update_record = GeneratedUpdate(
            project_id=project.id,
            idea_id=req.idea_id,
            topic=draft.topic,
            update_copy=draft.update_copy,
            relevant_keywords=",".join(draft.relevant_keywords) if isinstance(draft.relevant_keywords, list) else draft.relevant_keywords,
            call_to_action=draft.call_to_action,
            image_concept=draft.image_concept,
            ai_provider=provider_inst.provider_name,
            model_used=provider_inst.default_model,
            created_at=datetime.now(timezone.utc)
        )
        db.add(update_record)
        db.commit()
        db.refresh(update_record)

        return GeneratedUpdateResponse.model_validate(update_record)
