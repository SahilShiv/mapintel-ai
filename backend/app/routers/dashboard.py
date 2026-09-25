from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any, List
from collections import Counter

from backend.app.database import get_db
from backend.app.models.project import Project, Competitor
from backend.app.models.post import Post
from backend.app.models.scraping import ScrapingJob
from backend.app.models.content import GeneratedIdea, GeneratedUpdate
from backend.app.schemas.post import PostResponse
from backend.app.schemas.scraping import ScrapingJobResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("")
def get_dashboard_data(project_id: Optional[int] = None, db: Session = Depends(get_db)) -> Dict[str, Any]:
    # Base queries - only count valid, verified competitor posts
    proj_query = db.query(Project)
    comp_query = db.query(Competitor)
    post_query = db.query(Post).filter(Post.is_valid == True)
    job_query = db.query(ScrapingJob)
    idea_query = db.query(GeneratedIdea)
    update_query = db.query(GeneratedUpdate)

    if project_id:
        comp_query = comp_query.filter(Competitor.project_id == project_id)
        post_query = post_query.filter(Post.project_id == project_id)
        job_query = job_query.filter(ScrapingJob.project_id == project_id)
        idea_query = idea_query.filter(GeneratedIdea.project_id == project_id)
        update_query = update_query.filter(GeneratedUpdate.project_id == project_id)

    total_projects = proj_query.count()
    total_competitors = comp_query.count()
    total_posts = post_query.count()

    latest_job = job_query.order_by(ScrapingJob.start_time.desc()).first()
    new_posts_latest = latest_job.new_posts if latest_job else 0
    duplicates_skipped_latest = latest_job.duplicates_skipped if latest_job else 0

    total_duplicates_skipped = db.query(func.sum(ScrapingJob.duplicates_skipped)).scalar() or 0
    failed_attempts = db.query(func.sum(ScrapingJob.failures)).scalar() or 0

    generated_ideas_count = idea_query.count()
    generated_updates_count = update_query.count()
    total_generated_content = generated_ideas_count + generated_updates_count

    # Recent scraping activity
    recent_jobs = job_query.order_by(ScrapingJob.start_time.desc()).limit(5).all()

    # Latest competitor posts
    recent_posts = post_query.order_by(Post.published_date.desc()).limit(6).all()

    # Calculate Top Topics and Keywords across posts
    all_posts = post_query.all()
    topic_counter = Counter([p.industry_topic for p in all_posts if p.industry_topic])
    top_topics = [{"topic": t, "count": c} for t, c in topic_counter.most_common(5)]

    keyword_counter = Counter()
    for p in all_posts:
        if p.detected_keywords:
            for k in p.detected_keywords.split(","):
                k_clean = k.strip().lower()
                if len(k_clean) > 2:
                    keyword_counter[k_clean] += 1
    top_keywords = [{"keyword": k, "count": c} for k, c in keyword_counter.most_common(8)]

    # Competitor post counts
    comp_activity = []
    comps = comp_query.limit(8).all()
    for c in comps:
        count = sum(1 for p in all_posts if p.competitor_id == c.id)
        comp_activity.append({
            "id": c.id,
            "name": c.business_name,
            "post_count": count,
            "status": c.scraping_status
        })

    return {
        "kpis": {
            "total_projects": total_projects,
            "total_competitors": total_competitors,
            "total_posts": total_posts,
            "new_posts_latest": new_posts_latest,
            "duplicate_posts_skipped": total_duplicates_skipped,
            "failed_attempts": failed_attempts,
            "generated_content_count": total_generated_content
        },
        "recent_jobs": [ScrapingJobResponse.model_validate(j) for j in recent_jobs],
        "recent_posts": [PostResponse.model_validate(p) for p in recent_posts],
        "top_topics": top_topics,
        "top_keywords": top_keywords,
        "competitor_activity": comp_activity,
        "ai_overview": "Competitor activity is concentrated on promotional campaigns and seasonal tips. Active posts showcase consistent photo attachments."
    }
