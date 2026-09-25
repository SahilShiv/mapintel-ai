from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.app.database import get_db
from backend.app.models.project import Competitor
from backend.app.models.post import Post
from backend.app.schemas.competitor import CompetitorUpdate, CompetitorResponse
from backend.app.schemas.post import PostResponse
from backend.app.schemas.scraping import ScrapingJobResponse
from backend.app.services.scraper_service import ScraperService

router = APIRouter(prefix="/competitors", tags=["competitors"])

@router.get("/{id}", response_model=CompetitorResponse)
def get_competitor(id: int, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return CompetitorResponse.model_validate(comp)

@router.put("/{id}", response_model=CompetitorResponse)
def update_competitor(id: int, data: CompetitorUpdate, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    if data.business_name is not None:
        comp.business_name = data.business_name
    if data.google_maps_url is not None:
        comp.google_maps_url = data.google_maps_url
    if data.place_identifier is not None:
        comp.place_identifier = data.place_identifier
    if data.status is not None:
        comp.status = data.status

    db.commit()
    db.refresh(comp)
    return CompetitorResponse.model_validate(comp)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_competitor(id: int, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    db.delete(comp)
    db.commit()
    return None

@router.get("/{id}/posts", response_model=List[PostResponse])
def get_competitor_posts(id: int, db: Session = Depends(get_db)):
    comp = db.query(Competitor).filter(Competitor.id == id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    posts = db.query(Post).filter(Post.competitor_id == id).order_by(Post.published_date.desc()).all()
    return [PostResponse.model_validate(p) for p in posts]

@router.post("/{id}/scrape", response_model=ScrapingJobResponse)
def scrape_competitor(id: int, mode: str = "demo", db: Session = Depends(get_db)):
    """Scrapes or re-scrapes an individual competitor profile."""
    comp = db.query(Competitor).filter(Competitor.id == id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")
    job = ScraperService.scrape_single_competitor(competitor_id=id, db=db, mode=mode)
    return ScrapingJobResponse.model_validate(job)
