"""
Duplicate Detection Engine
Generates canonical fingerprints and queries database to skip identical updates.
"""

from typing import Optional, Set
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models.post import Post
from backend.app.services.fingerprint import generate_post_fingerprint

class DuplicateDetector:
    def __init__(self, db: Optional[Session] = None, project_id: Optional[int] = None):
        self.db = db
        self.project_id = project_id
        self._existing_fingerprints: Set[str] = set()
        if db:
            query = db.query(Post.fingerprint)
            if project_id:
                query = query.filter(Post.project_id == project_id)
            for row in query.all():
                self._existing_fingerprints.add(row[0])

    def compute_fingerprint(
        self,
        post_url: Optional[str],
        source_post_id: Optional[str],
        competitor_name: str,
        post_text: Optional[str],
        published_date: Optional[datetime],
        profile_url: Optional[str]
    ) -> str:
        return generate_post_fingerprint(
            post_url=post_url,
            source_post_id=source_post_id,
            competitor_name=competitor_name,
            post_text=post_text,
            published_date=published_date,
            profile_url=profile_url
        )

    def is_duplicate(self, fingerprint: str) -> bool:
        if fingerprint in self._existing_fingerprints:
            return True
        if self.db:
            exists = self.db.query(Post.id).filter(Post.fingerprint == fingerprint).first() is not None
            if exists:
                self._existing_fingerprints.add(fingerprint)
                return True
        return False

    def mark_seen(self, fingerprint: str):
        self._existing_fingerprints.add(fingerprint)
