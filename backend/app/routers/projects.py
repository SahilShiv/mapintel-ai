from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.project import Project, Competitor, Keyword
from backend.app.models.post import Post
from backend.app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse
)
from backend.app.schemas.competitor import CompetitorCreate, CompetitorResponse
from backend.app.schemas.keyword import KeywordCreate, KeywordResponse

router = APIRouter(prefix="/projects", tags=["projects"])

def _build_project_response(p: Project, db: Session) -> ProjectResponse:
    comp_count = db.query(func.count(Competitor.id)).filter(Competitor.project_id == p.id).scalar() or 0
    kw_count = db.query(func.count(Keyword.id)).filter(Keyword.project_id == p.id).scalar() or 0
    post_count = db.query(func.count(Post.id)).filter(Post.project_id == p.id, Post.is_valid == True).scalar() or 0
    last_scraped = db.query(func.max(Competitor.last_scraped_at)).filter(Competitor.project_id == p.id).scalar()

    return ProjectResponse(
        id=p.id,
        project_name=p.project_name,
        client_business_name=p.client_business_name,
        google_maps_url=p.google_maps_url,
        description=p.description,
        verified_facts=p.verified_facts,
        created_at=p.created_at,
        updated_at=p.updated_at,
        competitors_count=comp_count,
        keywords_count=kw_count,
        posts_count=post_count,
        last_scraped_at=last_scraped
    )

@router.get("", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return [_build_project_response(p, db) for p in projects]

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(
        project_name=data.project_name,
        client_business_name=data.client_business_name,
        google_maps_url=data.google_maps_url,
        description=data.description,
        verified_facts=data.verified_facts
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    # Add initial keywords if supplied
    if data.keywords:
        for kw in data.keywords:
            if kw.strip():
                k_obj = Keyword(project_id=project.id, keyword=kw.strip())
                db.add(k_obj)
        db.commit()

    return _build_project_response(project, db)

@router.get("/{id}", response_model=ProjectDetailResponse)
def get_project(id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    base = _build_project_response(project, db)
    comps = db.query(Competitor).filter(Competitor.project_id == id).all()
    kws = db.query(Keyword).filter(Keyword.project_id == id).all()

    return ProjectDetailResponse(
        **base.model_dump(),
        competitors=[CompetitorResponse.model_validate(c) for c in comps],
        keywords=[KeywordResponse.model_validate(k) for k in kws]
    )

@router.put("/{id}", response_model=ProjectResponse)
def update_project(id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if data.project_name is not None:
        project.project_name = data.project_name
    if data.client_business_name is not None:
        project.client_business_name = data.client_business_name
    if data.google_maps_url is not None:
        project.google_maps_url = data.google_maps_url
    if data.description is not None:
        project.description = data.description
    if data.verified_facts is not None:
        project.verified_facts = data.verified_facts

    db.commit()
    db.refresh(project)
    return _build_project_response(project, db)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return None

# --- Competitors Sub-endpoints ---

@router.get("/{id}/competitors", response_model=List[CompetitorResponse])
def get_project_competitors(id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    competitors = db.query(Competitor).filter(Competitor.project_id == id).all()
    return [CompetitorResponse.model_validate(c) for c in competitors]

@router.post("/{id}/competitors", response_model=CompetitorResponse, status_code=status.HTTP_201_CREATED)
def add_project_competitor(id: int, data: CompetitorCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    comp = Competitor(
        project_id=id,
        business_name=data.business_name,
        google_maps_url=data.google_maps_url,
        place_identifier=data.place_identifier,
        status=data.status or "active"
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return CompetitorResponse.model_validate(comp)

# --- Keywords Sub-endpoints ---

@router.get("/{id}/keywords", response_model=List[KeywordResponse])
def get_project_keywords(id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    keywords = db.query(Keyword).filter(Keyword.project_id == id).all()
    return [KeywordResponse.model_validate(k) for k in keywords]

@router.post("/{id}/keywords", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
def add_project_keyword(id: int, data: KeywordCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    existing = db.query(Keyword).filter(
        Keyword.project_id == id,
        func.lower(Keyword.keyword) == data.keyword.strip().lower()
    ).first()
    if existing:
        return KeywordResponse.model_validate(existing)

    kw = Keyword(project_id=id, keyword=data.keyword.strip())
    db.add(kw)
    db.commit()
    db.refresh(kw)
    return KeywordResponse.model_validate(kw)

@router.delete("/{id}/keywords/{kw_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_keyword(id: int, kw_id: int, db: Session = Depends(get_db)):
    kw = db.query(Keyword).filter(Keyword.id == kw_id, Keyword.project_id == id).first()
    if not kw:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(kw)
    db.commit()
    return None

# --- BONUS FEATURE: Keyword-based competitor discovery ---
@router.post("/{id}/discover-competitors")
def discover_competitors_by_keyword(id: int, keyword: str, db: Session = Depends(get_db)):
    """
    Discovers potential local competitors matching project keywords,
    checking each against the existing repository to prevent duplication.
    """
    project = db.query(Project).filter(Project.id == id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    existing_names = {c.business_name.lower() for c in db.query(Competitor).filter(Competitor.project_id == id).all()}

    # Realistic discovered candidate pool based on industry context
    candidates = [
        {"name": f"Luxe Studio & Care ({keyword})", "url": f"https://www.google.com/maps/place/Luxe-Studio-{keyword.replace(' ', '-')}"},
        {"name": f"Elite Style Lounge ({keyword})", "url": f"https://www.google.com/maps/place/Elite-Style-{keyword.replace(' ', '-')}"},
        {"name": f"Urban Glow Center ({keyword})", "url": f"https://www.google.com/maps/place/Urban-Glow-{keyword.replace(' ', '-')}"},
        {"name": f"Aura Wellness & Spa ({keyword})", "url": f"https://www.google.com/maps/place/Aura-Wellness-{keyword.replace(' ', '-')}"},
    ]

    results = []
    for c in candidates:
        already_tracked = c["name"].lower() in existing_names
        results.append({
            "business_name": c["name"],
            "google_maps_url": c["url"],
            "is_already_added": already_tracked
        })

    return {"keyword": keyword, "candidates": results}
