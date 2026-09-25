from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.app.database import get_db
from backend.app.models.project import Project
from backend.app.schemas.analysis import AnalysisTriggerRequest
from backend.app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["analysis"])

@router.post("")
def trigger_analysis(req: AnalysisTriggerRequest, db: Session = Depends(get_db)):
    """Runs AI analysis on stored competitor posts for a project."""
    project = db.query(Project).filter(Project.id == req.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    result = AnalysisService.analyze_project_posts(
        project_id=req.project_id,
        db=db,
        force_reanalyze=req.force_reanalyze or False,
        preferred_provider=req.provider
    )
    return result

@router.get("/{project_id}")
def get_project_analysis_summary(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    trends = AnalysisService.get_trend_analytics(project_id=project_id, db=db)
    return trends
