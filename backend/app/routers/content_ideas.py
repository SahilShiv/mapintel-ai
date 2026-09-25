from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.content import GeneratedIdea
from backend.app.schemas.content import (
    ContentIdeaRequest,
    ContentIdeaBatchResponse,
    GeneratedIdeaResponse
)
from backend.app.services.content_service import ContentService

router = APIRouter(prefix="/content-ideas", tags=["content-ideas"])

@router.post("", response_model=ContentIdeaBatchResponse)
def generate_ideas(req: ContentIdeaRequest, db: Session = Depends(get_db)):
    """
    Generates user-selected count (3, 5, 10, 20, 50) of content ideas
    based on competitor repository and prevents repeating existing ideas.
    """
    return ContentService.generate_content_ideas(req=req, db=db)

@router.get("", response_model=List[GeneratedIdeaResponse])
def get_generated_ideas(
    project_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(GeneratedIdea)
    if project_id:
        query = query.filter(GeneratedIdea.project_id == project_id)
    ideas = query.order_by(GeneratedIdea.created_at.desc()).limit(limit).all()
    return [GeneratedIdeaResponse.model_validate(i) for i in ideas]

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_idea(id: int, db: Session = Depends(get_db)):
    idea = db.query(GeneratedIdea).filter(GeneratedIdea.id == id).first()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    db.delete(idea)
    db.commit()
    return None
