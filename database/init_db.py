#!/usr/bin/env python3
"""
database/init_db.py
===================
Initialise the PostgreSQL schema from a clean environment.

Usage:
    python database/init_db.py [--drop-existing]

Options:
    --drop-existing   Drop and recreate all tables (DESTRUCTIVE — use only in dev).

Credentials are read from the .env file (never hard-coded).
"""

import argparse
import os
import sys
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.common.config import settings
from preprocessing.common.db import get_connection
from preprocessing.common.logging_utils import get_logger

logger = get_logger(__name__)

SCHEMA_FILE = Path(__file__).parent / "schema.sql"


def drop_all(conn) -> None:
    """Drop all project tables and types in reverse dependency order."""
    logger.warning("Dropping all tables and types — THIS IS DESTRUCTIVE.")
    statements = [
        # Tables (reverse FK order)
        "DROP TABLE IF EXISTS data_quality_issues CASCADE;",
        "DROP TABLE IF EXISTS processing_jobs CASCADE;",
        "DROP TABLE IF EXISTS readings CASCADE;",
        "DROP TABLE IF EXISTS transcript_segments CASCADE;",
        "DROP TABLE IF EXISTS transcripts CASCADE;",
        "DROP TABLE IF EXISTS video_segments CASCADE;",
        "DROP TABLE IF EXISTS videos CASCADE;",
        "DROP TABLE IF EXISTS assets CASCADE;",
        "DROP TABLE IF EXISTS lessons CASCADE;",
        "DROP TABLE IF EXISTS lesson_groups CASCADE;",
        "DROP TABLE IF EXISTS course_modules CASCADE;",
        "DROP TABLE IF EXISTS courses CASCADE;",
        # Triggers
        "DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;",
        # Enum types
        "DROP TYPE IF EXISTS timestamp_confidence_enum CASCADE;",
        "DROP TYPE IF EXISTS chunk_type_enum CASCADE;",
        "DROP TYPE IF EXISTS reading_subtype_enum CASCADE;",
        "DROP TYPE IF EXISTS transcript_format_enum CASCADE;",
        "DROP TYPE IF EXISTS dq_category_enum CASCADE;",
        "DROP TYPE IF EXISTS dq_severity_enum CASCADE;",
        "DROP TYPE IF EXISTS job_status_enum CASCADE;",
        "DROP TYPE IF EXISTS job_type_enum CASCADE;",
        "DROP TYPE IF EXISTS lesson_type_enum CASCADE;",
        "DROP TYPE IF EXISTS asset_category_enum CASCADE;",
        "DROP TYPE IF EXISTS processing_status_enum CASCADE;",
    ]
    with conn.cursor() as cur:
        for stmt in statements:
            cur.execute(stmt)
    conn.commit()
    logger.info("All tables and types dropped.")


def apply_schema(conn) -> None:
    """Execute schema.sql against the target database."""
    sql = SCHEMA_FILE.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    logger.info("Schema applied successfully from %s", SCHEMA_FILE)


def verify_tables(conn) -> list[str]:
    """Return list of table names created in the public schema."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_type = 'BASE TABLE'
            ORDER BY table_name;
            """
        )
        return [row[0] for row in cur.fetchall()]


def main(drop_existing: bool = False) -> int:
    logger.info("Connecting to database: %s@%s:%s/%s",
                settings.db_user, settings.db_host, settings.db_port, settings.db_name)

    try:
        conn = get_connection()
    except Exception as exc:
        logger.error("Could not connect to PostgreSQL: %s", exc)
        logger.error("Check your .env credentials and ensure PostgreSQL is running.")
        return 1

    try:
        if drop_existing:
            drop_all(conn)

        logger.info("Applying schema from %s …", SCHEMA_FILE)
        apply_schema(conn)

        tables = verify_tables(conn)
        logger.info("Tables present in database (%d):", len(tables))
        for t in tables:
            logger.info("  [OK] %s", t)

        logger.info("Database initialisation complete.")
        return 0

    except Exception as exc:
        conn.rollback()
        logger.error("Schema application failed: %s", exc)
        return 1

    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialise the Coursera platform database schema.")
    parser.add_argument(
        "--drop-existing",
        action="store_true",
        help="Drop all tables before applying schema (DESTRUCTIVE — dev only).",
    )
    args = parser.parse_args()
    sys.exit(main(drop_existing=args.drop_existing))
