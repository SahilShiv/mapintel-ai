from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.content import GeneratedUpdate
from backend.app.schemas.content import (
    GenerateUpdateRequest,
    GeneratedUpdateResponse
)
from backend.app.services.content_service import ContentService

router = APIRouter(prefix="", tags=["generated-updates"])

@router.post("/generate-update", response_model=GeneratedUpdateResponse)
@router.post("/generated-updates", response_model=GeneratedUpdateResponse)
def generate_update(req: GenerateUpdateRequest, db: Session = Depends(get_db)):
    """
    Generates a complete, publish-ready Google Maps update
    with copy, call-to-action, relevant keywords, and image concept.
    """
    return ContentService.generate_complete_update(req=req, db=db)

@router.get("/generated-updates", response_model=List[GeneratedUpdateResponse])
def get_generated_updates(
    project_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(GeneratedUpdate)
    if project_id:
        query = query.filter(GeneratedUpdate.project_id == project_id)
    updates = query.order_by(GeneratedUpdate.created_at.desc()).limit(limit).all()
    return [GeneratedUpdateResponse.model_validate(u) for u in updates]

@router.delete("/generated-updates/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_update(id: int, db: Session = Depends(get_db)):
    rec = db.query(GeneratedUpdate).filter(GeneratedUpdate.id == id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Generated update not found")
    db.delete(rec)
    db.commit()
    return None
