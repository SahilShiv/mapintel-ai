from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.database import get_db
from backend.app.models.scraping import ScrapingJob
from backend.app.models.project import Competitor
from backend.app.schemas.scraping import (
    ScrapingTriggerRequest,
    ScrapingJobResponse,
)
from backend.app.services.scraper_service import ScraperService

router = APIRouter(prefix="/scrape", tags=["scraping"])

@router.post("", response_model=ScrapingJobResponse)
def trigger_scrape(
    req: ScrapingTriggerRequest,
    background_tasks: BackgroundTasks,
    sync: bool = Query(False, description="If True, executes synchronously instead of background"),
    db: Session = Depends(get_db)
):
    """
    Starts an asynchronous scraping job for a project and its competitors.
    Returns immediately with a pending ScrapingJob record so the browser never freezes.
    The frontend polls GET /scrape/jobs/{id} until completion.
    """
    if sync or req.sync:
        job = ScraperService.run_scraping_job(
            project_id=req.project_id,
            db=db,
            competitor_ids=req.competitor_ids,
            mode=req.mode or "demo"
        )
        return ScrapingJobResponse.model_validate(job)

    job = ScraperService.create_pending_job(
        project_id=req.project_id,
        db=db,
        competitor_ids=req.competitor_ids,
        mode=req.mode or "demo"
    )

    # Launch execution asynchronously in background
    background_tasks.add_task(
        ScraperService.execute_job,
        job_id=job.id,
        competitor_ids=req.competitor_ids,
        simulate_captcha=False
    )

    return ScrapingJobResponse.model_validate(job)

@router.post("/demo", response_model=ScrapingJobResponse)
def trigger_demo_scrape(
    project_id: int,
    background_tasks: BackgroundTasks,
    simulate_captcha: bool = False,
    sync: bool = Query(False, description="If True, executes synchronously instead of background"),
    db: Session = Depends(get_db)
):
    """
    Starts a high-fidelity Demo Scrape asynchronously.
    Enforces real duplicate detection, job logging, and progress updates.
    """
    if sync:
        job = ScraperService.run_scraping_job(
            project_id=project_id,
            db=db,
            mode="demo",
            simulate_captcha=simulate_captcha
        )
        return ScrapingJobResponse.model_validate(job)

    job = ScraperService.create_pending_job(
        project_id=project_id,
        db=db,
        mode="demo"
    )

    background_tasks.add_task(
        ScraperService.execute_job,
        job_id=job.id,
        competitor_ids=None,
        simulate_captcha=simulate_captcha
    )

    return ScrapingJobResponse.model_validate(job)

@router.get("/jobs", response_model=List[ScrapingJobResponse])
def get_scraping_jobs(
    project_id: Optional[int] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(ScrapingJob)
    if project_id:
        query = query.filter(ScrapingJob.project_id == project_id)
    jobs = query.order_by(ScrapingJob.start_time.desc()).limit(limit).all()
    return [ScrapingJobResponse.model_validate(j) for j in jobs]

@router.get("/jobs/{id}", response_model=ScrapingJobResponse)
def get_scraping_job(id: int, db: Session = Depends(get_db)):
    job = db.query(ScrapingJob).filter(ScrapingJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Scraping job not found")
    return ScrapingJobResponse.model_validate(job)

@router.post("/jobs/{id}/continue", response_model=ScrapingJobResponse)
def continue_after_captcha(
    id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Resumes or resolves a scraping job after user confirms manual verification
    or switches to demo mode.
    """
    job = db.query(ScrapingJob).filter(ScrapingJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Scraping job not found")

    # Reset competitor captcha status
    competitors = db.query(Competitor).filter(
        Competitor.project_id == job.project_id,
        Competitor.scraping_status == "captcha_required"
    ).all()
    for c in competitors:
        c.scraping_status = "idle"
    db.commit()

    # Create resumed job
    resumed_job = ScraperService.create_pending_job(
        project_id=job.project_id,
        db=db,
        mode="demo"
    )

    background_tasks.add_task(
        ScraperService.execute_job,
        job_id=resumed_job.id,
        competitor_ids=None,
        simulate_captcha=False
    )

    return ScrapingJobResponse.model_validate(resumed_job)
