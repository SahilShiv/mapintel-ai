import logging
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models.project import Project, Competitor
from backend.app.models.post import Post, PostMedia, InvalidScrapedRecord
from backend.app.models.scraping import ScrapingJob, ScrapingJobItem
from backend.app.services.fingerprint import generate_post_fingerprint
from backend.app.services.scraper.google_maps_scraper import GoogleMapsSeleniumScraper
from backend.app.services.scraper.demo_scraper import DemoGoogleMapsScraper
from backend.app.services.scraper.validation import PostContentValidator
from backend.app.services.scraper.base import ScrapeResult

logger = logging.getLogger(__name__)

class ScraperService:
    @staticmethod
    def create_pending_job(
        project_id: int,
        db: Session,
        competitor_ids: Optional[List[int]] = None,
        mode: str = "demo"
    ) -> ScrapingJob:
        """
        Creates an initial ScrapingJob record in 'Pending' state so API can return immediately
        without waiting on browser automation or long network requests.
        """
        comp_query = db.query(Competitor).filter(Competitor.project_id == project_id)
        if competitor_ids:
            comp_query = comp_query.filter(Competitor.id.in_(competitor_ids))
        total_comps = comp_query.count()

        job = ScrapingJob(
            project_id=project_id,
            job_type=mode.upper(),
            status="Pending",
            start_time=datetime.now(timezone.utc),
            total_competitors=total_comps,
            competitors_processed=0,
            posts_found=0,
            valid_posts=0,
            new_posts=0,
            duplicates_skipped=0,
            images_downloaded=0,
            failures=0,
            captcha_detected=False
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @classmethod
    def execute_job(
        cls,
        job_id: int,
        competitor_ids: Optional[List[int]] = None,
        simulate_captcha: bool = False,
        db: Optional[Session] = None
    ):
        """
        Background worker that executes the scraping workflow for a job ID.
        Uses the provided session or creates its own to be fully safe for background tasks.
        """
        owns_db = False
        if db is None:
            db = SessionLocal()
            owns_db = True
        try:
            job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
            if not job:
                logger.error(f"Scraping job {job_id} not found in background worker")
                return

            job.status = "Running"
            db.commit()

            project = db.query(Project).filter(Project.id == job.project_id).first()
            if not project:
                job.status = "Failed"
                job.error_details = f"Project {job.project_id} not found"
                job.end_time = datetime.now(timezone.utc)
                db.commit()
                return

            comp_query = db.query(Competitor).filter(Competitor.project_id == job.project_id)
            if competitor_ids:
                comp_query = comp_query.filter(Competitor.id.in_(competitor_ids))
            competitors = comp_query.all()

            if not competitors:
                job.status = "Completed"
                job.end_time = datetime.now(timezone.utc)
                db.commit()
                return

            is_live = job.job_type.upper() == "LIVE"
            src_label = "LIVE" if is_live else "DEMO"

            scraper = (
                GoogleMapsSeleniumScraper()
                if is_live
                else DemoGoogleMapsScraper(simulate_captcha=simulate_captcha)
            )

            extraction_failure_count = 0

            for comp in competitors:
                comp.scraping_status = "running"
                db.commit()

                try:
                    result: ScrapeResult = scraper.scrape_competitor(
                        competitor_id=comp.id,
                        competitor_name=comp.business_name,
                        google_maps_url=comp.google_maps_url,
                        job_id=job.id
                    )

                    # 1. Handle CAPTCHA checkpoint
                    if result.captcha_detected or result.status == "captcha_required":
                        job.captcha_detected = True
                        job.status = "Manual Intervention Required"
                        job.error_details = (
                            f"Google Maps security verification required for '{comp.business_name}'. "
                            "Please complete verification in browser or switch to Demo mode."
                        )
                        comp.scraping_status = "captcha_required"

                        job_item = ScrapingJobItem(
                            job_id=job.id,
                            competitor_id=comp.id,
                            competitor_name=comp.business_name,
                            status="CAPTCHA_REQUIRED",
                            posts_found=0,
                            valid_posts=0,
                            new_posts=0,
                            duplicates_skipped=0,
                            error_message=result.error_message or "Security verification encountered",
                            log_message=result.log_message or "CAPTCHA required",
                            timestamp=datetime.now(timezone.utc)
                        )
                        db.add(job_item)
                        db.commit()
                        break

                    # 2. Handle extraction failure (selectors failed or UI garbage rejected)
                    if result.status == "extraction_failed" or (result.status == "success" and result.posts_found == 0):
                        extraction_failure_count += 1
                        comp.scraping_status = "extraction_failed"

                        fail_msg = result.error_message or "Google Maps Updates/Post content could not be reliably identified."
                        job_item = ScrapingJobItem(
                            job_id=job.id,
                            competitor_id=comp.id,
                            competitor_name=comp.business_name,
                            status="EXTRACTION_FAILED",
                            posts_found=0,
                            valid_posts=0,
                            new_posts=0,
                            duplicates_skipped=0,
                            error_message=fail_msg,
                            log_message=f"Extraction failed for {comp.business_name}: {fail_msg}",
                            timestamp=datetime.now(timezone.utc)
                        )
                        db.add(job_item)
                        job.competitors_processed += 1
                        db.commit()
                        continue

                    # 3. Process candidate posts through strict PostContentValidator
                    comp_valid_posts = 0
                    comp_new_posts = 0
                    comp_duplicates = 0
                    comp_images = 0

                    for post_data in result.posts:
                        is_valid, reason = PostContentValidator.validate(post_data.post_text)

                        if not is_valid:
                            # Record invalid record so it can be audited, but NEVER insert into repository
                            invalid_rec = InvalidScrapedRecord(
                                project_id=project.id,
                                competitor_id=comp.id,
                                competitor_name=comp.business_name,
                                raw_text=post_data.post_text[:1000] if post_data.post_text else "",
                                rejection_reason=reason or "Failed post content validation",
                                source_type=src_label,
                                created_at=datetime.now(timezone.utc)
                            )
                            db.add(invalid_rec)
                            continue

                        comp_valid_posts += 1

                        # Duplicate Detection via Cryptographic Fingerprint
                        clean_text = PostContentValidator.clean_text(post_data.post_text)
                        fp = generate_post_fingerprint(
                            post_url=post_data.post_url,
                            source_post_id=post_data.source_post_id,
                            competitor_name=comp.business_name,
                            post_text=clean_text,
                            published_date=post_data.published_date,
                            profile_url=comp.google_maps_url
                        )

                        existing = db.query(Post).filter(Post.fingerprint == fp).first()
                        if existing:
                            comp_duplicates += 1
                            continue

                        # Clean authentic post insertion
                        new_post = Post(
                            project_id=project.id,
                            competitor_id=comp.id,
                            competitor_name=comp.business_name,
                            google_maps_profile_url=comp.google_maps_url,
                            post_url=post_data.post_url,
                            post_text=clean_text,
                            published_date=post_data.published_date or datetime.now(timezone.utc),
                            call_to_action=post_data.call_to_action or "Learn More",
                            detected_keywords=",".join(post_data.detected_keywords) if post_data.detected_keywords else None,
                            industry_topic=post_data.industry_topic or "General",
                            content_type=post_data.content_type or "Update",
                            source_information=src_label,
                            source_type=src_label,
                            is_valid=True,
                            fingerprint=fp,
                            scraped_at=datetime.now(timezone.utc)
                        )
                        db.add(new_post)
                        db.flush()

                        for img_url in post_data.media_urls:
                            if PostContentValidator.is_valid_image_url(img_url):
                                media = PostMedia(
                                    post_id=new_post.id,
                                    media_type="image",
                                    media_url=img_url
                                )
                                db.add(media)
                                comp_images += 1

                        comp_new_posts += 1

                    # Update competitor status & counters
                    comp.total_posts = comp.total_posts + comp_new_posts
                    comp.last_scraped_at = datetime.now(timezone.utc)
                    comp.scraping_status = "completed" if comp_valid_posts > 0 else "extraction_failed"

                    # Update running job counters
                    job.competitors_processed += 1
                    job.posts_found += result.posts_found
                    job.valid_posts += comp_valid_posts
                    job.new_posts += comp_new_posts
                    job.duplicates_skipped += comp_duplicates
                    job.images_downloaded += comp_images

                    item_status = "SUCCESS" if comp_valid_posts > 0 else "EXTRACTION_FAILED"
                    item_msg = (
                        f"Processed {comp.business_name}: {comp_valid_posts} valid posts ({comp_new_posts} new, {comp_duplicates} duplicates skipped)."
                        if comp_valid_posts > 0
                        else f"Extraction failed for {comp.business_name}: No valid updates identified."
                    )

                    job_item = ScrapingJobItem(
                        job_id=job.id,
                        competitor_id=comp.id,
                        competitor_name=comp.business_name,
                        status=item_status,
                        posts_found=result.posts_found,
                        valid_posts=comp_valid_posts,
                        new_posts=comp_new_posts,
                        duplicates_skipped=comp_duplicates,
                        log_message=item_msg,
                        timestamp=datetime.now(timezone.utc)
                    )
                    db.add(job_item)
                    db.commit()

                except Exception as comp_err:
                    logger.error(f"Error scraping competitor {comp.business_name}: {comp_err}", exc_info=True)
                    comp.scraping_status = "error"
                    job.competitors_processed += 1
                    job.failures += 1

                    job_item = ScrapingJobItem(
                        job_id=job.id,
                        competitor_id=comp.id,
                        competitor_name=comp.business_name,
                        status="FAILED",
                        posts_found=0,
                        valid_posts=0,
                        new_posts=0,
                        duplicates_skipped=0,
                        error_message=str(comp_err),
                        log_message=f"Scraper error: {str(comp_err)}",
                        timestamp=datetime.now(timezone.utc)
                    )
                    db.add(job_item)
                    db.commit()

            # Finalize overall job status
            if job.status != "Manual Intervention Required":
                if job.valid_posts == 0 and len(competitors) > 0:
                    job.status = "Extraction Failed"
                    job.error_details = "Google Maps Updates/Post content could not be reliably identified across competitors."
                elif job.failures > 0 or extraction_failure_count > 0:
                    job.status = "Partial Success"
                else:
                    job.status = "Completed"

            job.end_time = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"Finished scraping job {job.id} with status {job.status}")

        except Exception as e:
            logger.error(f"Fatal error in scraping job {job_id}: {e}", exc_info=True)
            try:
                job = db.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
                if job:
                    job.status = "Failed"
                    job.error_details = str(e)
                    job.end_time = datetime.now(timezone.utc)
                    db.commit()
            except Exception:
                pass
        finally:
            if owns_db:
                db.close()

    @classmethod
    def run_scraping_job(
        cls,
        project_id: int,
        db: Session,
        competitor_ids: Optional[List[int]] = None,
        mode: str = "demo",
        simulate_captcha: bool = False
    ) -> ScrapingJob:
        """
        Synchronous wrapper: creates the job and executes it immediately.
        Used for tests, scripts, or local CLI executions.
        """
        job = cls.create_pending_job(
            project_id=project_id,
            db=db,
            competitor_ids=competitor_ids,
            mode=mode
        )
        cls.execute_job(
            job_id=job.id,
            competitor_ids=competitor_ids,
            simulate_captcha=simulate_captcha,
            db=db
        )
        db.refresh(job)
        return job
