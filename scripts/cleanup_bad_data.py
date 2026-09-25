"""
Cleanup and Migration Utility for Scraped Posts
Scans the database for posts containing Google Maps UI garbage, navigation labels,
or page-wide innerText dumps. Flags them as is_valid = False and copies them
to the invalid_scraped_records audit table.
"""

import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.migrate import run_migrations
from backend.app.models.post import Post, InvalidScrapedRecord
from backend.app.services.scraper.validation import PostContentValidator

def cleanup_bad_scraped_data():
    run_migrations()
    db = SessionLocal()
    try:
        print("Auditing existing database records for Google Maps UI text garbage...")
        all_posts = db.query(Post).all()
        print(f"Found {len(all_posts)} total posts to inspect.")

        cleaned_count = 0
        valid_count = 0

        for post in all_posts:
            is_valid, reason = PostContentValidator.validate(post.post_text)

            if not is_valid:
                print(f"[REJECTED] Post #{post.id} ({post.competitor_name}): {reason}")
                post.is_valid = False
                post.validation_error = reason

                # Ensure it is recorded in invalid_scraped_records
                exists = db.query(InvalidScrapedRecord).filter(
                    InvalidScrapedRecord.raw_text == post.post_text[:1000]
                ).first()
                if not exists:
                    inv = InvalidScrapedRecord(
                        project_id=post.project_id,
                        competitor_id=post.competitor_id,
                        competitor_name=post.competitor_name,
                        raw_text=post.post_text[:1000] if post.post_text else "",
                        rejection_reason=reason or "UI garbage cleanup",
                        source_type=getattr(post, "source_type", "DEMO")
                    )
                    db.add(inv)
                cleaned_count += 1
            else:
                post.is_valid = True
                post.validation_error = None
                valid_count += 1

        db.commit()
        print("--------------------------------------------------")
        print(f"Cleanup finished: {valid_count} valid posts confirmed, {cleaned_count} invalid records quarantined.")
        print("--------------------------------------------------")
        return cleaned_count == 0
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_bad_scraped_data()
