from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.project import Project
from backend.app.schemas.analysis import TrendAnalysisResponse
from backend.app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/trends", tags=["trends"])

@router.get("/{project_id}", response_model=TrendAnalysisResponse)
def get_trends(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    trends = AnalysisService.get_trend_analytics(project_id=project_id, db=db)
    return trends
