"""
Database Data Quality Audit Script
Validates all stored records against integrity requirements:
- Empty post text
- Page-wide Google Maps UI text
- Duplicate fingerprints
- Invalid dates
- Missing competitor
- Missing project
- Invalid URLs
- Duplicate generated ideas
- AI records without source posts

Produces PASS or FAIL with itemized details.
"""

import sys
import os
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.migrate import run_migrations
from backend.app.models.project import Project, Competitor
from backend.app.models.post import Post, PostAnalysis
from backend.app.models.content import GeneratedIdea, GeneratedUpdate
from backend.app.services.scraper.validation import PostContentValidator

def audit_database() -> bool:
    run_migrations()
    db = SessionLocal()
    problems = []

    print("==================================================")
    print("      DATABASE DATA QUALITY AUDIT - MAPINTEL AI   ")
    print("==================================================")

    try:
        # 1. Inspect Projects & Competitors
        projects = db.query(Project).all()
        project_ids = {p.id for p in projects}
        if not projects:
            problems.append("CRITICAL: No projects found in database.")

        competitors = db.query(Competitor).all()
        competitor_ids = {c.id for c in competitors}
        for c in competitors:
            if c.project_id not in project_ids:
                problems.append(f"Competitor #{c.id} ('{c.business_name}') references missing project #{c.project_id}.")
            if not c.google_maps_url or not c.google_maps_url.startswith("http"):
                problems.append(f"Competitor #{c.id} has invalid Google Maps URL: '{c.google_maps_url}'.")

        # 2. Inspect Posts
        all_posts = db.query(Post).all()
        valid_posts = [p for p in all_posts if p.is_valid]
        print(f"Total Posts: {len(all_posts)} ({len(valid_posts)} valid, {len(all_posts) - len(valid_posts)} invalid)")

        fingerprints = []
        for post in valid_posts:
            # Check empty post text
            if not post.post_text or not post.post_text.strip():
                problems.append(f"Post #{post.id} has empty post_text.")

            # Check for page-wide Google Maps text or UI garbage
            is_valid, reason = PostContentValidator.validate(post.post_text)
            if not is_valid:
                problems.append(f"Post #{post.id} ('{post.competitor_name}') contains Google Maps UI garbage: {reason}")

            # Check missing project
            if post.project_id not in project_ids:
                problems.append(f"Post #{post.id} references non-existent project #{post.project_id}.")

            # Check missing competitor
            if post.competitor_id not in competitor_ids:
                problems.append(f"Post #{post.id} references non-existent competitor #{post.competitor_id}.")

            # Check dates
            if not post.published_date:
                problems.append(f"Post #{post.id} has null published_date.")

            # Check URL
            if post.post_url and not (post.post_url.startswith("http://") or post.post_url.startswith("https://")):
                problems.append(f"Post #{post.id} has invalid post_url: '{post.post_url}'.")

            # Check fingerprint
            if not post.fingerprint:
                problems.append(f"Post #{post.id} is missing unique cryptographic fingerprint.")
            else:
                fingerprints.append(post.fingerprint)

        # Check duplicate fingerprints among valid posts
        fp_counts = Counter(fingerprints)
        duplicates = [fp for fp, count in fp_counts.items() if count > 1]
        if duplicates:
            problems.append(f"Found {len(duplicates)} duplicate post fingerprints among valid posts: {duplicates[:3]}")

        # 3. Check AI Analysis Records without source posts
        analysis_records = db.query(PostAnalysis).all()
        post_ids = {p.id for p in all_posts}
        for a in analysis_records:
            if a.post_id not in post_ids:
                problems.append(f"PostAnalysis #{a.id} references non-existent post #{a.post_id}.")

        # 4. Check Generated Content Ideas for duplicates
        ideas = db.query(GeneratedIdea).all()
        idea_hashes = []
        for idea in ideas:
            if idea.project_id not in project_ids:
                problems.append(f"GeneratedIdea #{idea.id} references non-existent project #{idea.project_id}.")
            if not idea.title or not idea.title.strip():
                problems.append(f"GeneratedIdea #{idea.id} has empty title.")
            if idea.semantic_hash:
                idea_hashes.append((idea.project_id, idea.semantic_hash))

        hash_counts = Counter(idea_hashes)
        dup_ideas = [h for h, count in hash_counts.items() if count > 1]
        if dup_ideas:
            problems.append(f"Found {len(dup_ideas)} duplicate generated ideas within the same project.")

        # 5. Check Generated Updates
        updates = db.query(GeneratedUpdate).all()
        for u in updates:
            if u.project_id not in project_ids:
                problems.append(f"GeneratedUpdate #{u.id} references non-existent project #{u.project_id}.")
            if not u.update_copy or not u.update_copy.strip():
                problems.append(f"GeneratedUpdate #{u.id} has empty update copy.")

        # Report Outcome
        print("--------------------------------------------------")
        if problems:
            print("FAIL")
            print(f"Total problems identified: {len(problems)}")
            for idx, p in enumerate(problems, 1):
                print(f"  {idx}. {p}")
            print("--------------------------------------------------")
            return False
        else:
            print("PASS")
            print("All repository data checks passed with zero integrity defects:")
            print(f"  [OK] {len(projects)} projects verified")
            print(f"  [OK] {len(competitors)} competitors verified")
            print(f"  [OK] {len(valid_posts)} clean competitor posts verified")
            print(f"  [OK] Zero Google Maps page UI text found")
            print(f"  [OK] Zero duplicate post fingerprints")
            print(f"  [OK] {len(ideas)} unique content ideas verified")
            print(f"  [OK] {len(analysis_records)} AI analysis records verified")
            print("--------------------------------------------------")
            return True

    finally:
        db.close()

if __name__ == "__main__":
    passed = audit_database()
    sys.exit(0 if passed else 1)
