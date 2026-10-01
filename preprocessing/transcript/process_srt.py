"""
preprocessing/transcript/process_srt.py
=========================================
Step 6 — Parse and store SRT (SubRip) transcript files.

For each .en.srt file:
  1. Parse SubRip blocks (sequence number, timestamps, text).
  2. Validate: sequential numbers, start < end, non-empty text.
  3. Clean formatting artifacts.
  4. Store each block as a transcript_segment (chunk_type='srt_caption').
  5. Preserve exact timestamps.

Usage:
    python preprocessing/transcript/process_srt.py
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from preprocessing.common.db import get_db
from preprocessing.common.logging_utils import get_logger
from preprocessing.common.models import SRTBlock, TimestampConfidence, ChunkType
from preprocessing.common.utils import count_tokens, normalize_whitespace

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# SRT parsing
# ---------------------------------------------------------------------------

SRT_TIMESTAMP_RE = re.compile(
    r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*"
    r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})"
)

HTML_TAG_RE = re.compile(r"<[^>]+>")  # strip inline formatting tags


def parse_timestamp(h: str, m: str, s: str, ms: str) -> float:
    """Convert SRT timestamp components to float seconds."""
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def clean_srt_text(text: str) -> str:
    """Remove HTML tags and excessive whitespace from SRT caption text."""
    text = HTML_TAG_RE.sub("", text)
    text = normalize_whitespace(text)
    return text


def parse_srt_content(content: str) -> list[SRTBlock]:
    """
    Parse raw SRT content into a list of SRTBlock objects.
    Handles malformed blocks gracefully.
    """
    blocks: list[SRTBlock] = []
    # Split on double newlines (block separator)
    raw_blocks = re.split(r"\n{2,}", content.strip())

    for raw in raw_blocks:
        lines = [l.strip() for l in raw.strip().splitlines() if l.strip()]
        if len(lines) < 2:
            continue

        # Sequence number
        try:
            seq = int(lines[0])
        except ValueError:
            continue  # not a valid SRT block

        # Timestamp line
        ts_match = SRT_TIMESTAMP_RE.match(lines[1]) if len(lines) > 1 else None
        if not ts_match:
            continue

        start = parse_timestamp(*ts_match.groups()[:4])
        end   = parse_timestamp(*ts_match.groups()[4:])

        # Text (remaining lines after timestamp)
        raw_text = " ".join(lines[2:])
        text = clean_srt_text(raw_text)

        if not text:
            continue

        try:
            block = SRTBlock(
                sequence_number=seq,
                start_seconds=start,
                end_seconds=end,
                text=text,
            )
            blocks.append(block)
        except Exception as exc:
            logger.warning("SRTBlock validation error (seq=%s): %s", seq, exc)
            continue

    return blocks


def parse_srt_file(path: Path) -> list[SRTBlock]:
    """Read an SRT file and return parsed blocks. Handles encoding issues."""
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning("UTF-8 decode failed for %s — trying latin-1.", path.name)
        content = path.read_text(encoding="latin-1")

    blocks = parse_srt_content(content)
    logger.debug("Parsed %d SRT blocks from %s", len(blocks), path.name)
    return blocks


def validate_srt_blocks(blocks: list[SRTBlock]) -> list[str]:
    """
    Validate SRT blocks and return a list of issue descriptions.
    """
    issues = []
    for i, blk in enumerate(blocks):
        if i > 0:
            prev = blocks[i - 1]
            if blk.sequence_number != prev.sequence_number + 1:
                issues.append(
                    f"Non-sequential block: expected {prev.sequence_number + 1}, got {blk.sequence_number}"
                )
            if blk.start_seconds < prev.start_seconds:
                issues.append(
                    f"Block {blk.sequence_number}: start_seconds ({blk.start_seconds}) "
                    f"< previous start_seconds ({prev.start_seconds})"
                )
        if blk.end_seconds < blk.start_seconds:
            issues.append(
                f"Block {blk.sequence_number}: end ({blk.end_seconds}) < start ({blk.start_seconds})"
            )
        if not blk.text.strip():
            issues.append(f"Block {blk.sequence_number}: empty text")
    return issues


# ---------------------------------------------------------------------------
# DB operations
# ---------------------------------------------------------------------------

def store_srt_transcript(
    asset_id: str,
    video_asset_id: Optional[str],
    blocks: list[SRTBlock],
    cleaned_text: str,
    conn,
) -> None:
    """Upsert the transcript record and all its segment rows."""
    char_count = len(cleaned_text)
    word_count = len(cleaned_text.split())
    line_count = len(blocks)

    # Upsert transcript
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO transcripts (
                id, video_asset_id, source_format, language_code,
                char_count, word_count, line_count, has_timestamps,
                encoding, cleaned_text, extracted_at
            ) VALUES (
                %(id)s, %(video_asset_id)s, 'srt', 'en',
                %(char_count)s, %(word_count)s, %(line_count)s, TRUE,
                'utf-8', %(cleaned_text)s, NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                char_count   = EXCLUDED.char_count,
                word_count   = EXCLUDED.word_count,
                line_count   = EXCLUDED.line_count,
                cleaned_text = EXCLUDED.cleaned_text,
                extracted_at = NOW()
            """,
            {
                "id":            asset_id,
                "video_asset_id": video_asset_id,
                "char_count":    char_count,
                "word_count":    word_count,
                "line_count":    line_count,
                "cleaned_text":  cleaned_text,
            },
        )

    # Delete old segments, re-insert (idempotent)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM transcript_segments WHERE transcript_id = %s", (asset_id,))

    seg_rows = [
        {
            "transcript_id":       asset_id,
            "segment_index":       blk.sequence_number - 1,
            "text":                blk.text,
            "chunk_type":          ChunkType.SRT_CAPTION.value,
            "start_time_seconds":  blk.start_seconds,
            "end_time_seconds":    blk.end_seconds,
            "timestamp_confidence": TimestampConfidence.HIGH.value,
            "srt_sequence_number": blk.sequence_number,
            "token_count":         count_tokens(blk.text),
            "start_char":          None,
            "end_char":            None,
        }
        for blk in blocks
    ]
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO transcript_segments (
                transcript_id, segment_index, text, chunk_type,
                start_time_seconds, end_time_seconds, timestamp_confidence,
                srt_sequence_number, token_count, start_char, end_char
            ) VALUES (
                %(transcript_id)s, %(segment_index)s, %(text)s, %(chunk_type)s,
                %(start_time_seconds)s, %(end_time_seconds)s, %(timestamp_confidence)s,
                %(srt_sequence_number)s, %(token_count)s, %(start_char)s, %(end_char)s
            )
            """,
            seg_rows,
        )


def find_video_asset_id(srt_slug: str, conn) -> Optional[str]:
    """Find the video asset whose slug matches this SRT's video counterpart."""
    video_slug = re.sub(r'\.en\.srt$', '.mp4', srt_slug)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM assets WHERE asset_slug = %s LIMIT 1", (video_slug,)
        )
        row = cur.fetchone()
    return str(row[0]) if row else None


def process_all_srts() -> dict:
    """Process every SRT asset. Returns summary counters."""
    t0 = time.time()
    stats = {"total": 0, "succeeded": 0, "failed": 0, "skipped": 0, "issues": []}

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, asset_slug, extracted_path
                FROM assets
                WHERE asset_category = 'transcript_srt'
                ORDER BY asset_slug
                """
            )
            rows = cur.fetchall()

        logger.info("Processing %d SRT files …", len(rows))

        for (asset_id, asset_slug, extracted_path) in rows:
            stats["total"] += 1
            if not extracted_path or not Path(extracted_path).exists():
                logger.warning("SRT file not found: %s", extracted_path)
                stats["skipped"] += 1
                continue

            try:
                blocks = parse_srt_file(Path(extracted_path))

                if not blocks:
                    logger.warning("No SRT blocks parsed from %s", asset_slug)
                    stats["skipped"] += 1
                    continue

                validation_issues = validate_srt_blocks(blocks)
                for iss in validation_issues:
                    logger.warning("SRT issue in %s: %s", asset_slug, iss)
                    stats["issues"].append({"asset": asset_slug, "issue": iss})

                cleaned_text = "\n".join(b.text for b in blocks)
                video_asset_id = find_video_asset_id(asset_slug, conn)

                store_srt_transcript(str(asset_id), video_asset_id, blocks, cleaned_text, conn)

                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE assets SET processing_status = 'processed' WHERE id = %s",
                        (asset_id,),
                    )
                stats["succeeded"] += 1

            except Exception as exc:
                logger.error("Failed SRT processing %s: %s", asset_slug, exc)
                stats["failed"] += 1

    elapsed_ms = int((time.time() - t0) * 1000)
    logger.info(
        "SRT processing done in %dms — %d ok / %d failed / %d skipped",
        elapsed_ms, stats["succeeded"], stats["failed"], stats["skipped"],
    )
    return stats


if __name__ == "__main__":
    results = process_all_srts()
    sys.exit(0 if results["failed"] == 0 else 1)
