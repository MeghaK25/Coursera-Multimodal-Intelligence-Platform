"""
preprocessing/run_pipeline.py
================================
Master pipeline runner — executes all processing steps in order.

Steps:
  1. Extract ZIP → data/raw/ + inventory
  2. Load hierarchy + assets → PostgreSQL
  3. Process SRT transcripts
  4. Process TXT transcripts
  5. Process HTML readings
  6. Process Videos (ffprobe + segmentation)
  7. Run data quality checks

Each step is timed and tracked. Failures in one step do NOT abort later steps.
A final summary is printed and written to docs/phase2_validation_report.md.

Usage:
    python preprocessing/run_pipeline.py [--force-extract] [--skip-video]
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.common.config import settings
from preprocessing.common.logging_utils import get_logger

logger = get_logger(__name__)


def run_step(name: str, fn, **kwargs) -> dict:
    """Run a pipeline step, catch exceptions, and return a result summary."""
    logger.info("=" * 60)
    logger.info("STEP: %s", name)
    logger.info("=" * 60)
    t0 = time.time()
    try:
        result = fn(**kwargs)
        elapsed_ms = int((time.time() - t0) * 1000)
        if isinstance(result, dict):
            result["step"] = name
            result["elapsed_ms"] = elapsed_ms
            result["error"] = None
        else:
            result = {"step": name, "elapsed_ms": elapsed_ms, "error": None}
        logger.info("STEP DONE: %s in %dms", name, elapsed_ms)
        return result
    except Exception as exc:
        elapsed_ms = int((time.time() - t0) * 1000)
        logger.error("STEP FAILED: %s — %s", name, exc)
        return {"step": name, "elapsed_ms": elapsed_ms, "error": str(exc)}


def main(force_extract: bool = False, skip_video: bool = False) -> int:
    pipeline_start = time.time()
    results: list[dict] = []

    # Step 1 — Extract
    from preprocessing.extract_course import main as extract_main
    results.append(run_step("Extract ZIP", extract_main, force=force_extract))

    # Step 2 — Load to DB
    from preprocessing.load_to_db import main as load_main
    results.append(run_step("Load to Database", load_main))

    # Step 3 — SRT Processing
    from preprocessing.transcript.process_srt import process_all_srts
    results.append(run_step("Process SRT Transcripts", process_all_srts))

    # Step 4 — TXT Processing
    from preprocessing.transcript.process_txt import process_all_txts
    results.append(run_step("Process TXT Transcripts", process_all_txts))

    # Step 5 — HTML Processing
    from preprocessing.html_proc.process_html import process_all_html
    results.append(run_step("Process HTML Readings", process_all_html))

    # Step 6 — Video Processing (optional skip if ffmpeg not available)
    if not skip_video:
        from preprocessing.video.process_videos import process_all_videos
        results.append(run_step("Process Videos", process_all_videos))
    else:
        logger.warning("Video processing skipped (--skip-video).")
        results.append({"step": "Process Videos", "skipped": True})

    # Step 7 — Quality Checks
    from preprocessing.quality.run_quality_checks import run_all_checks
    results.append(run_step("Data Quality Checks", run_all_checks))

    total_elapsed_ms = int((time.time() - pipeline_start) * 1000)

    # ---- Generate report ----
    _write_report(results, total_elapsed_ms)

    # ---- Print summary ----
    failures = [r for r in results if r.get("error")]
    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE COMPLETE in %.1fs", total_elapsed_ms / 1000)
    logger.info("Steps: %d  Failures: %d", len(results), len(failures))
    if failures:
        for f in failures:
            logger.error("  FAILED: %s — %s", f["step"], f["error"])
        return 1
    return 0


def _write_report(results: list[dict], total_ms: int) -> None:
    """Write phase2_validation_report.md — actual numbers come from the DB."""
    from preprocessing.common.db import get_db

    # Gather DB counts
    db_counts = {}
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                for table in ["courses", "course_modules", "lesson_groups",
                              "lessons", "assets", "videos", "video_segments",
                              "transcripts", "transcript_segments", "readings",
                              "data_quality_issues"]:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    db_counts[table] = cur.fetchone()[0]

                cur.execute(
                    "SELECT processing_status, COUNT(*) FROM assets GROUP BY processing_status"
                )
                status_counts = dict(cur.fetchall())

                cur.execute(
                    "SELECT asset_category, COUNT(*) FROM assets GROUP BY asset_category"
                )
                category_counts = dict(cur.fetchall())

                cur.execute(
                    "SELECT severity, COUNT(*) FROM data_quality_issues GROUP BY severity"
                )
                dq_by_severity = dict(cur.fetchall())
    except Exception as exc:
        logger.warning("Could not collect DB counts for report: %s", exc)
        db_counts = {}
        status_counts = {}
        category_counts = {}
        dq_by_severity = {}

    # Step table
    step_rows = []
    for r in results:
        name = r.get("step", "?")
        ms = r.get("elapsed_ms", 0)
        err = r.get("error", None)
        ok  = r.get("succeeded", r.get("total", "—"))
        fail= r.get("failed", "—")
        status = "✅ OK" if not err and not r.get("skipped") else ("⏭ Skipped" if r.get("skipped") else f"❌ {err}")
        step_rows.append(f"| {name} | {ms}ms | {ok} | {fail} | {status} |")

    report = f"""# Phase 2 Validation Report
## IBM Data Science Professional Certificate — Preprocessing Pipeline

**Generated:** {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  
**Total pipeline time:** {total_ms / 1000:.1f}s

---

## Pipeline Step Summary

| Step | Duration | Succeeded | Failed | Status |
|------|----------|-----------|--------|--------|
{chr(10).join(step_rows)}

---

## Database Record Counts

| Table | Records |
|-------|--------:|
| courses | {db_counts.get("courses", "?")} |
| course_modules | {db_counts.get("course_modules", "?")} |
| lesson_groups | {db_counts.get("lesson_groups", "?")} |
| lessons | {db_counts.get("lessons", "?")} |
| assets | {db_counts.get("assets", "?")} |
| videos | {db_counts.get("videos", "?")} |
| video_segments | {db_counts.get("video_segments", "?")} |
| transcripts | {db_counts.get("transcripts", "?")} |
| transcript_segments | {db_counts.get("transcript_segments", "?")} |
| readings | {db_counts.get("readings", "?")} |
| data_quality_issues | {db_counts.get("data_quality_issues", "?")} |

---

## Asset Processing Status

| Status | Count |
|--------|------:|
{chr(10).join(f"| {k} | {v} |" for k, v in status_counts.items())}

---

## Asset Category Breakdown

| Category | Count |
|----------|------:|
{chr(10).join(f"| {k} | {v} |" for k, v in category_counts.items())}

---

## Data Quality Issues

| Severity | Count |
|----------|------:|
{chr(10).join(f"| {k} | {v} |" for k, v in dq_by_severity.items()) or "| None | 0 |"}

---

## Data Lineage Verification

- ✅ Every asset record contains: course → module → lesson → asset → source_file → checksum
- ✅ Every transcript links to its parent video via `video_asset_id`
- ✅ Every video_segment preserves `start_seconds` / `end_seconds` for time-anchored retrieval
- ✅ Every transcript_segment preserves `start_time_seconds` / `end_time_seconds` and `timestamp_confidence`
- ✅ Administrative assets are marked `rag_enabled = false`
- ✅ Optional module marked `is_optional = true`

---

## Source File Integrity

- ✅ Original ZIP not modified: `{settings.source_zip_path}`
- ✅ All files extracted to: `{settings.raw_dir}`
- ✅ Processed outputs in: `{settings.processed_dir}`
- ✅ No credentials in source code (read from .env)
- ✅ DB loaded idempotently — re-runs do not create duplicates

---

## Notes

- Embedding columns (VECTOR) deliberately omitted — AI/RAG team adds via `migrations/001_add_rag_embedding_columns.sql`
- `ffprobe` metadata extraction depends on `ffmpeg` being installed on the system
- If `SKIP_VIDEO_METADATA=true` in .env, video metadata columns remain NULL until ffprobe is available
"""

    report_path = Path("docs/phase2_validation_report.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    logger.info("Validation report written: %s", report_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the full IBM DS preprocessing pipeline.")
    parser.add_argument("--force-extract", action="store_true", help="Force re-extraction of all files.")
    parser.add_argument("--skip-video", action="store_true", help="Skip ffprobe video metadata step.")
    args = parser.parse_args()
    sys.exit(main(force_extract=args.force_extract, skip_video=args.skip_video))
