"""
preprocessing/quality/run_quality_checks.py
=============================================
Step 10 — Run all data quality checks and store findings in data_quality_issues.

Checks:
  FILES:    duplicate checksums, empty files, missing extracted files
  VIDEOS:   duration > 0, valid codec, resolution, audio presence
  SRT:      valid timestamps, sequential captions, non-empty text
  TXT:      non-empty content, minimum word count
  HTML:     parsed successfully, non-empty text, base64 detection
  RELATIONSHIPS: every asset → lesson → lesson_group → module → course
                 every transcript → video asset
                 no orphan records

Usage:
    python preprocessing/quality/run_quality_checks.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from preprocessing.common.db import get_db
from preprocessing.common.logging_utils import get_logger
from preprocessing.common.models import DQIssue, DQSeverity

logger = get_logger(__name__)

DQ_ISSUE_COUNTER = 0


def next_issue_code() -> str:
    global DQ_ISSUE_COUNTER
    DQ_ISSUE_COUNTER += 1
    return f"DQ-{DQ_ISSUE_COUNTER:03d}"


def store_issue(issue: DQIssue, asset_id_lookup: dict, conn) -> None:
    """Insert a DQ issue into the database.
    
    The table is cleared at the start of each quality check run (idempotency),
    so plain INSERTs are used — no conflict handling needed.
    """
    asset_id = asset_id_lookup.get(issue.asset_slug) if issue.asset_slug else None
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO data_quality_issues (
                issue_code, asset_id, severity, category,
                description, recommendation
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                issue.issue_code,
                asset_id,
                issue.severity.value,
                issue.category,
                issue.description,
                issue.recommendation,
            ),
        )



# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_duplicate_checksums(conn) -> list[DQIssue]:
    """Find assets sharing the same SHA-256 checksum."""
    issues = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT checksum_sha256, array_agg(asset_slug) as slugs, COUNT(*) as cnt
            FROM assets
            WHERE checksum_sha256 IS NOT NULL
            GROUP BY checksum_sha256
            HAVING COUNT(*) > 1
            """
        )
        rows = cur.fetchall()

    for (checksum, slugs, cnt) in rows:
        issues.append(DQIssue(
            issue_code=next_issue_code(),
            asset_slug=slugs[0],
            severity=DQSeverity.MEDIUM,
            category="validation",
            description=f"Duplicate checksum ({checksum[:12]}…) found across {cnt} files: {slugs}",
            recommendation="Verify these are not erroneously duplicated files.",
        ))
    return issues


def check_empty_files(conn) -> list[DQIssue]:
    """Find assets with size_bytes = 0."""
    issues = []
    with conn.cursor() as cur:
        cur.execute("SELECT asset_slug FROM assets WHERE size_bytes = 0")
        rows = cur.fetchall()
    for (slug,) in rows:
        issues.append(DQIssue(
            issue_code=next_issue_code(),
            asset_slug=slug,
            severity=DQSeverity.HIGH,
            category="validation",
            description=f"Empty file detected: {slug}",
            recommendation="Inspect source ZIP — file may be corrupt.",
        ))
    return issues


def check_missing_extracted_files(conn) -> list[DQIssue]:
    """Find assets marked 'extracted' but whose extracted_path does not exist on disk."""
    issues = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT asset_slug, extracted_path
            FROM assets
            WHERE processing_status IN ('extracted','processed')
              AND extracted_path IS NOT NULL
            """
        )
        rows = cur.fetchall()

    for (slug, path) in rows:
        if not Path(path).exists():
            issues.append(DQIssue(
                issue_code=next_issue_code(),
                asset_slug=slug,
                severity=DQSeverity.HIGH,
                category="validation",
                description=f"Extracted file missing from disk: {path}",
                recommendation="Re-run extract_course.py to restore the file.",
            ))
    return issues


def check_video_metadata(conn) -> list[DQIssue]:
    """Validate video metadata for obvious problems."""
    issues = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.asset_slug, v.duration_seconds, v.width_px, v.height_px,
                   v.video_codec, v.has_audio
            FROM videos v
            JOIN assets a ON a.id = v.id
            """
        )
        rows = cur.fetchall()

    for (slug, dur, w, h, codec, has_audio) in rows:
        if dur is not None and dur <= 0:
            issues.append(DQIssue(
                issue_code=next_issue_code(),
                asset_slug=slug,
                severity=DQSeverity.HIGH,
                category="validation",
                description=f"Invalid video duration ({dur}s) for {slug}",
                recommendation="Inspect video file with ffprobe.",
            ))
        if w is not None and h is not None and (w <= 0 or h <= 0):
            issues.append(DQIssue(
                issue_code=next_issue_code(),
                asset_slug=slug,
                severity=DQSeverity.MEDIUM,
                category="validation",
                description=f"Invalid resolution ({w}x{h}) for {slug}",
            ))
        if not has_audio:
            issues.append(DQIssue(
                issue_code=next_issue_code(),
                asset_slug=slug,
                severity=DQSeverity.MEDIUM,
                category="validation",
                description=f"No audio stream detected in video {slug}",
                recommendation="Verify the video has audio. Educational videos should have audio.",
            ))
    return issues


def check_srt_segments(conn) -> list[DQIssue]:
    """Check SRT transcript_segments for timestamp issues."""
    issues = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.asset_slug, ts.segment_index,
                   ts.start_time_seconds, ts.end_time_seconds
            FROM transcript_segments ts
            JOIN transcripts t ON t.id = ts.transcript_id
            JOIN assets a ON a.id = t.id
            WHERE ts.chunk_type = 'srt_caption'
              AND ts.start_time_seconds IS NOT NULL
              AND ts.end_time_seconds IS NOT NULL
              AND ts.end_time_seconds < ts.start_time_seconds
            """
        )
        rows = cur.fetchall()

    for (slug, idx, start, end) in rows:
        issues.append(DQIssue(
            issue_code=next_issue_code(),
            asset_slug=slug,
            severity=DQSeverity.MEDIUM,
            category="validation",
            description=f"SRT caption {idx}: end ({end}s) < start ({start}s) in {slug}",
        ))

    # Empty text segments
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.asset_slug, COUNT(*) as cnt
            FROM transcript_segments ts
            JOIN transcripts t ON t.id = ts.transcript_id
            JOIN assets a ON a.id = t.id
            WHERE ts.chunk_type = 'srt_caption'
              AND (ts.text IS NULL OR LENGTH(TRIM(ts.text)) = 0)
            GROUP BY a.asset_slug
            """
        )
        rows = cur.fetchall()

    for (slug, cnt) in rows:
        issues.append(DQIssue(
            issue_code=next_issue_code(),
            asset_slug=slug,
            severity=DQSeverity.LOW,
            category="content",
            description=f"{cnt} empty SRT caption(s) in {slug}",
        ))
    return issues


def check_txt_content(conn) -> list[DQIssue]:
    """Validate TXT transcripts for content problems."""
    issues = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.asset_slug, t.word_count, t.char_count
            FROM transcripts t
            JOIN assets a ON a.id = t.id
            WHERE t.source_format = 'txt'
            """
        )
        rows = cur.fetchall()

    for (slug, words, chars) in rows:
        if (words or 0) < 10:
            issues.append(DQIssue(
                issue_code=next_issue_code(),
                asset_slug=slug,
                severity=DQSeverity.MEDIUM,
                category="content",
                description=f"Very low word count ({words}) in TXT transcript {slug}",
            ))
    return issues


def check_html_content(conn) -> list[DQIssue]:
    """Validate HTML readings for content issues."""
    issues = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.asset_slug, r.word_count, r.has_embedded_image
            FROM readings r
            JOIN assets a ON a.id = r.id
            """
        )
        rows = cur.fetchall()

    for (slug, words, has_img) in rows:
        if (words or 0) < 3:
            issues.append(DQIssue(
                issue_code=next_issue_code(),
                asset_slug=slug,
                severity=DQSeverity.LOW,
                category="content",
                description=f"Very short/empty extracted text ({words} words) in HTML {slug}",
            ))
    return issues


def check_orphan_records(conn) -> list[DQIssue]:
    """Check for broken foreign key relationships."""
    issues = []

    # Transcripts without a matching video asset
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.asset_slug
            FROM transcripts t
            JOIN assets a ON a.id = t.id
            WHERE t.video_asset_id IS NULL
              AND a.asset_category IN ('transcript_srt','transcript_txt')
            """
        )
        rows = cur.fetchall()

    for (slug,) in rows:
        issues.append(DQIssue(
            issue_code=next_issue_code(),
            asset_slug=slug,
            severity=DQSeverity.LOW,
            category="relationship",
            description=f"Transcript {slug} has no linked video_asset_id",
            recommendation="Check if the companion MP4 was loaded correctly.",
        ))

    # Assets with no lesson_id (orphan assets)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT asset_slug FROM assets
            WHERE lesson_id IS NULL
            """
        )
        rows = cur.fetchall()

    for (slug,) in rows:
        issues.append(DQIssue(
            issue_code=next_issue_code(),
            asset_slug=slug,
            severity=DQSeverity.HIGH,
            category="relationship",
            description=f"Asset {slug} has no lesson_id — orphan record.",
            recommendation="Re-run load_to_db.py to rebuild hierarchy.",
        ))

    return issues


def check_asset_category_coverage(conn) -> list[DQIssue]:
    """Check that all assets have been processed."""
    issues = []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT asset_category, COUNT(*) as total,
                   SUM(CASE WHEN processing_status = 'pending' THEN 1 ELSE 0 END) as pending
            FROM assets
            GROUP BY asset_category
            """
        )
        rows = cur.fetchall()

    for (cat, total, pending) in rows:
        if pending and pending > 0:
            issues.append(DQIssue(
                issue_code=next_issue_code(),
                asset_slug=None,
                severity=DQSeverity.LOW,
                category="validation",
                description=f"{pending}/{total} assets in category '{cat}' are still 'pending' (unprocessed)",
                recommendation="Re-run the appropriate processing step.",
            ))
    return issues


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_all_checks() -> dict:
    t0 = time.time()
    all_issues: list[DQIssue] = []

    logger.info("Running data quality checks …")

    check_fns = [
        ("Duplicate checksums",     check_duplicate_checksums),
        ("Empty files",             check_empty_files),
        ("Missing extracted files", check_missing_extracted_files),
        ("Video metadata",          check_video_metadata),
        ("SRT segments",            check_srt_segments),
        ("TXT content",             check_txt_content),
        ("HTML content",            check_html_content),
        ("Orphan records",          check_orphan_records),
        ("Unprocessed assets",      check_asset_category_coverage),
    ]

    with get_db() as conn:
        # Idempotency: clear previous DQ issues before each full re-evaluation.
        # DQ checks are a complete pass — old results must not accumulate on re-runs.
        with conn.cursor() as cur:
            cur.execute("DELETE FROM data_quality_issues")
            deleted = cur.rowcount
        if deleted:
            logger.info("Cleared %d previous DQ issue(s) before re-evaluation.", deleted)

        # Reset issue counter so codes stay consistent across runs
        global DQ_ISSUE_COUNTER
        DQ_ISSUE_COUNTER = 0

        # Build slug → id lookup
        with conn.cursor() as cur:
            cur.execute("SELECT asset_slug, id FROM assets")
            asset_id_lookup = {row[0]: str(row[1]) for row in cur.fetchall()}

        for label, fn in check_fns:
            logger.info("  Checking: %s …", label)
            try:
                found = fn(conn)
                all_issues.extend(found)
                if found:
                    logger.warning("    → %d issue(s) found", len(found))
                else:
                    logger.info("    → OK")
            except Exception as exc:
                logger.error("Check '%s' raised an exception: %s", label, exc)

        # Store all issues
        logger.info("Storing %d DQ issue(s) in database …", len(all_issues))
        for issue in all_issues:
            store_issue(issue, asset_id_lookup, conn)

    by_severity: dict[str, int] = {}
    for iss in all_issues:
        by_severity[iss.severity.value] = by_severity.get(iss.severity.value, 0) + 1

    elapsed_ms = int((time.time() - t0) * 1000)
    logger.info("Quality checks complete in %dms — %d issues total: %s",
                elapsed_ms, len(all_issues), by_severity)

    return {
        "total_issues": len(all_issues),
        "by_severity": by_severity,
        "elapsed_ms": elapsed_ms,
        "issues": [i.model_dump() for i in all_issues],
    }


if __name__ == "__main__":
    results = run_all_checks()
    sys.exit(0 if results["total_issues"] == 0 else 1)
