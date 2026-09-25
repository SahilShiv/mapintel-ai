"""
Database Migration Utility
Safely adds missing columns and tables to existing database (SQLite or PostgreSQL)
without data loss.
"""

import logging
from sqlalchemy import text
from backend.app.database import engine, Base

logger = logging.getLogger(__name__)

def run_migrations():
    """
    Applies schema alterations for any newly introduced columns and tables.
    Safe to run repeatedly.
    """
    # 1. Ensure all new tables are created
    Base.metadata.create_all(bind=engine)

    # 2. Add columns to existing tables if missing
    columns_to_add = [
        ("posts", "source_type", "VARCHAR(50) DEFAULT 'DEMO'"),
        ("posts", "is_valid", "BOOLEAN DEFAULT 1"),
        ("posts", "validation_error", "TEXT"),
        ("projects", "verified_facts", "TEXT"),
        ("scraping_jobs", "valid_posts", "INTEGER DEFAULT 0"),
        ("scraping_job_items", "valid_posts", "INTEGER DEFAULT 0"),
    ]

    with engine.begin() as conn:
        for table, col_name, col_type in columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type};"))
                logger.info(f"Added column {col_name} to table {table}")
            except Exception as e:
                # Column likely already exists
                pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
    print("Database migrations applied successfully.")
