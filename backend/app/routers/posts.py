from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional, List
from datetime import datetime
import math

from backend.app.database import get_db
from backend.app.models.post import Post, PostMedia, PostAnalysis, InvalidScrapedRecord
from backend.app.schemas.post import PostResponse, PostListResponse

router = APIRouter(prefix="/posts", tags=["posts"])

@router.get("", response_model=PostListResponse)
def get_posts(
    project_id: Optional[int] = None,
    competitor_id: Optional[int] = None,
    source_type: Optional[str] = None,
    search: Optional[str] = None,
    topic: Optional[str] = None,
    keyword: Optional[str] = None,
    content_type: Optional[str] = None,
    call_to_action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_invalid: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Retrieves filtered competitor posts from the repository.
    Strictly filters out invalid page UI extractions by default (is_valid == True).
    Supports comprehensive search, date ranges, topics, source types, and pagination.
    """
    query = db.query(Post)

    if not include_invalid:
        query = query.filter(Post.is_valid == True)

    if project_id:
        query = query.filter(Post.project_id == project_id)
    if competitor_id:
        query = query.filter(Post.competitor_id == competitor_id)
    if source_type:
        query = query.filter(Post.source_type.ilike(f"%{source_type}%"))
    if topic:
        query = query.filter(Post.industry_topic == topic)
    if keyword and keyword.strip():
        query = query.filter(Post.detected_keywords.ilike(f"%{keyword.strip()}%"))
    if content_type:
        query = query.filter(Post.content_type == content_type)
    if call_to_action:
        query = query.filter(Post.call_to_action == call_to_action)
    if start_date:
        query = query.filter(Post.published_date >= start_date)
    if end_date:
        query = query.filter(Post.published_date <= end_date)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Post.post_text.ilike(term),
                Post.competitor_name.ilike(term),
                Post.industry_topic.ilike(term),
                Post.detected_keywords.ilike(term)
            )
        )

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    posts = (
        query.order_by(Post.published_date.desc().nullslast(), Post.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PostListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=[PostResponse.model_validate(p) for p in posts]
    )

@router.get("/invalid-records")
def get_invalid_scraped_records(
    project_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Returns rejected scraping records that contained Google Maps UI text
    or failed validation, allowing auditors to inspect rejected items.
    """
    query = db.query(InvalidScrapedRecord)
    if project_id:
        query = query.filter(InvalidScrapedRecord.project_id == project_id)
    records = query.order_by(InvalidScrapedRecord.created_at.desc()).limit(limit).all()
    return [
        {
            "id": r.id,
            "project_id": r.project_id,
            "competitor_name": r.competitor_name,
            "raw_text_snippet": r.raw_text[:200] if r.raw_text else "",
            "rejection_reason": r.rejection_reason,
            "source_type": r.source_type,
            "created_at": r.created_at
        }
        for r in records
    ]

@router.get("/{id}", response_model=PostResponse)
def get_post_detail(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostResponse.model_validate(post)
