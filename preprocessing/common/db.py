"""
preprocessing/common/db.py
===========================
Database connection helpers using psycopg3.

All functions read credentials from settings (which reads .env).
Passwords are never logged.
"""

from __future__ import annotations

import contextlib
from typing import Generator

import psycopg

from preprocessing.common.config import settings
from preprocessing.common.logging_utils import get_logger

logger = get_logger(__name__)


def get_connection() -> psycopg.Connection:
    """Open and return a new psycopg3 Connection."""
    return psycopg.connect(settings.db_dsn)


@contextlib.contextmanager
def get_db() -> Generator[psycopg.Connection, None, None]:
    """
    Context manager that yields a connection and auto-commits on clean exit,
    rolls back on error, and closes on exit.

    Usage:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(...)
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def upsert_returning_id(
    conn: psycopg.Connection,
    table: str,
    data: dict,
    conflict_columns: list[str],
    returning: str = "id",
) -> str:
    """
    Generic INSERT ... ON CONFLICT DO UPDATE ... RETURNING <returning>.

    Returns the row's ID (existing or newly created).
    Prevents duplicate records on re-runs (idempotency).
    """
    cols = list(data.keys())
    placeholders = [f"%({c})s" for c in cols]
    updates = [f"{c} = EXCLUDED.{c}" for c in cols if c not in conflict_columns]

    sql = f"""
        INSERT INTO {table} ({', '.join(cols)})
        VALUES ({', '.join(placeholders)})
        ON CONFLICT ({', '.join(conflict_columns)})
        DO UPDATE SET {', '.join(updates) if updates else f'{conflict_columns[0]} = EXCLUDED.{conflict_columns[0]}'}
        RETURNING {returning}
    """
    with conn.cursor() as cur:
        cur.execute(sql, data)
        row = cur.fetchone()
        return str(row[0]) if row else None


def record_exists(
    conn: psycopg.Connection,
    table: str,
    column: str,
    value: str,
) -> bool:
    """Return True if a row with column=value already exists."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM {table} WHERE {column} = %s LIMIT 1", (value,))
        return cur.fetchone() is not None


def execute_many(
    conn: psycopg.Connection,
    sql: str,
    rows: list[dict],
) -> int:
    """Bulk-insert a list of dicts. Returns row count inserted."""
    if not rows:
        return 0
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
        return cur.rowcount
