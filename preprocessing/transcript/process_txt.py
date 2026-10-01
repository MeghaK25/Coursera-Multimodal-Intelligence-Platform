"""
preprocessing/transcript/process_txt.py
=========================================
Step 7 — Process plain-text transcript (.en.txt) files.

For each .en.txt file:
  1. Read with UTF-8 encoding (log failures).
  2. Normalize whitespace / line endings.
  3. Validate non-empty content.
  4. Chunk into ~500-token segments at sentence boundaries.
  5. Align chunks to SRT timestamps where possible.
  6. Store as transcript + transcript_segments.

Timestamp alignment strategy:
  - Build a cumulative text map from the SRT companion file.
  - For each TXT chunk, identify its approximate position in the
    total text by character offset ratio.
  - Map that ratio to the total video duration to get a start/end time.
  - If confidence >= SRT_ALIGN_CONFIDENCE_THRESHOLD → 'high', else 'low'.
  - If no SRT is available → timestamps NULL, confidence 'none'.

Usage:
    python preprocessing/transcript/process_txt.py
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from preprocessing.common.config import settings
from preprocessing.common.db import get_db
from preprocessing.common.logging_utils import get_logger
from preprocessing.common.models import ChunkType, TimestampConfidence
from preprocessing.common.utils import (
    count_tokens,
    normalize_whitespace,
    count_words,
)
from preprocessing.transcript.process_srt import parse_srt_file

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

SENTENCE_ENDINGS = re.compile(r'(?<=[.!?])\s+')


def split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation heuristics."""
    # Split on sentence-ending punctuation followed by whitespace
    parts = SENTENCE_ENDINGS.split(text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(
    text: str,
    target_tokens: int,
    overlap_tokens: int,
) -> list[dict]:
    """
    Split text into overlapping chunks of approximately `target_tokens` tokens.
    Prefers sentence boundaries.

    Returns list of dicts with keys:
        segment_index, text, start_char, end_char, token_count
    """
    sentences = split_into_sentences(text)
    chunks = []
    current_sentences: list[str] = []
    current_tokens = 0
    char_offset = 0

    # Build character offset map
    sentence_offsets: list[tuple[int, int]] = []  # (start_char, end_char)
    pos = 0
    for sent in sentences:
        start = text.find(sent, pos)
        if start == -1:
            start = pos
        end = start + len(sent)
        sentence_offsets.append((start, end))
        pos = end

    def flush_chunk(sents: list[str], sent_idxs: list[int]) -> dict:
        chunk_text_str = " ".join(sents)
        start_char = sentence_offsets[sent_idxs[0]][0] if sent_idxs else 0
        end_char   = sentence_offsets[sent_idxs[-1]][1] if sent_idxs else 0
        return {
            "text":       chunk_text_str,
            "start_char": start_char,
            "end_char":   end_char,
            "token_count": count_tokens(chunk_text_str),
        }

    current_sent_idxs: list[int] = []

    for i, sent in enumerate(sentences):
        sent_tokens = count_tokens(sent)

        if current_tokens + sent_tokens > target_tokens and current_sentences:
            chunk = flush_chunk(current_sentences, current_sent_idxs)
            chunk["segment_index"] = len(chunks)
            chunks.append(chunk)

            # Overlap: keep last N sentences that fit in overlap_tokens
            overlap_sents: list[str] = []
            overlap_idxs: list[int] = []
            overlap_tok = 0
            for s, si in zip(
                reversed(current_sentences), reversed(current_sent_idxs)
            ):
                t = count_tokens(s)
                if overlap_tok + t > overlap_tokens:
                    break
                overlap_sents.insert(0, s)
                overlap_idxs.insert(0, si)
                overlap_tok += t

            current_sentences = overlap_sents + [sent]
            current_sent_idxs = overlap_idxs + [i]
            current_tokens = overlap_tok + sent_tokens
        else:
            current_sentences.append(sent)
            current_sent_idxs.append(i)
            current_tokens += sent_tokens

    # Final chunk
    if current_sentences:
        chunk = flush_chunk(current_sentences, current_sent_idxs)
        chunk["segment_index"] = len(chunks)
        chunks.append(chunk)

    return chunks


# ---------------------------------------------------------------------------
# SRT timestamp alignment
# ---------------------------------------------------------------------------

def align_chunks_to_srt(
    chunks: list[dict],
    total_chars: int,
    srt_blocks,  # list[SRTBlock]
) -> list[dict]:
    """
    For each TXT chunk, estimate its time range by:
    1. Computing its fractional position in the text (char_offset / total_chars).
    2. Mapping that fraction to the SRT time range.
    3. Finding the SRT blocks that fall in that estimated time range.

    Sets start_time_seconds, end_time_seconds, timestamp_confidence.
    """
    if not srt_blocks or total_chars == 0:
        for c in chunks:
            c["start_time_seconds"] = None
            c["end_time_seconds"] = None
            c["timestamp_confidence"] = TimestampConfidence.NONE.value
        return chunks

    total_duration = srt_blocks[-1].end_seconds if srt_blocks else 0.0

    for c in chunks:
        start_frac = (c["start_char"] or 0) / total_chars
        end_frac   = (c["end_char"] or total_chars) / total_chars

        est_start = start_frac * total_duration
        est_end   = end_frac   * total_duration

        # Find SRT blocks overlapping the estimated time range
        overlapping = [
            b for b in srt_blocks
            if b.start_seconds < est_end and b.end_seconds > est_start
        ]

        if overlapping:
            c["start_time_seconds"] = overlapping[0].start_seconds
            c["end_time_seconds"]   = overlapping[-1].end_seconds
            c["timestamp_confidence"] = TimestampConfidence.LOW.value
        else:
            c["start_time_seconds"] = None
            c["end_time_seconds"]   = None
            c["timestamp_confidence"] = TimestampConfidence.NONE.value

    return chunks


# ---------------------------------------------------------------------------
# DB operations
# ---------------------------------------------------------------------------

def find_video_asset_id_for_txt(txt_slug: str, conn) -> Optional[str]:
    """Find the matching video asset id for a TXT transcript slug."""
    video_slug = re.sub(r'\.en\.txt$', '.mp4', txt_slug)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id FROM assets WHERE asset_slug = %s LIMIT 1", (video_slug,)
        )
        row = cur.fetchone()
    return str(row[0]) if row else None


def find_srt_path_for_txt(txt_slug: str, conn) -> Optional[Path]:
    """Find the extracted SRT path for the companion SRT file."""
    srt_slug = re.sub(r'\.en\.txt$', '.en.srt', txt_slug)
    with conn.cursor() as cur:
        cur.execute(
            "SELECT extracted_path FROM assets WHERE asset_slug = %s LIMIT 1",
            (srt_slug,),
        )
        row = cur.fetchone()
    if row and row[0]:
        p = Path(row[0])
        return p if p.exists() else None
    return None


def store_txt_transcript(
    asset_id: str,
    video_asset_id: Optional[str],
    chunks: list[dict],
    cleaned_text: str,
    conn,
) -> None:
    """Upsert transcript + all chunk segments."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO transcripts (
                id, video_asset_id, source_format, language_code,
                char_count, word_count, line_count, has_timestamps,
                encoding, cleaned_text, extracted_at
            ) VALUES (
                %(id)s, %(video_asset_id)s, 'txt', 'en',
                %(char_count)s, %(word_count)s, %(line_count)s, FALSE,
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
                "id":             asset_id,
                "video_asset_id": video_asset_id,
                "char_count":     len(cleaned_text),
                "word_count":     count_words(cleaned_text),
                "line_count":     cleaned_text.count("\n") + 1,
                "cleaned_text":   cleaned_text,
            },
        )

    with conn.cursor() as cur:
        cur.execute("DELETE FROM transcript_segments WHERE transcript_id = %s", (asset_id,))

    seg_rows = [
        {
            "transcript_id":       asset_id,
            "segment_index":       c["segment_index"],
            "text":                c["text"],
            "chunk_type":          ChunkType.TXT_WINDOW.value,
            "start_char":          c.get("start_char"),
            "end_char":            c.get("end_char"),
            "start_time_seconds":  c.get("start_time_seconds"),
            "end_time_seconds":    c.get("end_time_seconds"),
            "timestamp_confidence": c.get("timestamp_confidence", TimestampConfidence.NONE.value),
            "srt_sequence_number": None,
            "token_count":         c.get("token_count", 0),
        }
        for c in chunks
    ]
    with conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO transcript_segments (
                transcript_id, segment_index, text, chunk_type,
                start_char, end_char, start_time_seconds, end_time_seconds,
                timestamp_confidence, srt_sequence_number, token_count
            ) VALUES (
                %(transcript_id)s, %(segment_index)s, %(text)s, %(chunk_type)s,
                %(start_char)s, %(end_char)s, %(start_time_seconds)s, %(end_time_seconds)s,
                %(timestamp_confidence)s, %(srt_sequence_number)s, %(token_count)s
            )
            """,
            seg_rows,
        )


def process_all_txts() -> dict:
    """Process every TXT transcript asset. Returns summary counters."""
    t0 = time.time()
    stats = {"total": 0, "succeeded": 0, "failed": 0, "skipped": 0}

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, asset_slug, extracted_path
                FROM assets
                WHERE asset_category = 'transcript_txt'
                ORDER BY asset_slug
                """
            )
            rows = cur.fetchall()

        logger.info("Processing %d TXT transcript files …", len(rows))

        for (asset_id, asset_slug, extracted_path) in rows:
            stats["total"] += 1
            if not extracted_path or not Path(extracted_path).exists():
                logger.warning("TXT file not found: %s", extracted_path)
                stats["skipped"] += 1
                continue

            try:
                # Read and clean
                try:
                    raw = Path(extracted_path).read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    logger.warning("UTF-8 decode failed for %s — using chardet.", asset_slug)
                    import chardet
                    raw_bytes = Path(extracted_path).read_bytes()
                    detected = chardet.detect(raw_bytes)
                    raw = raw_bytes.decode(detected.get("encoding", "latin-1"), errors="replace")

                cleaned = normalize_whitespace(raw)

                if not cleaned or count_words(cleaned) < 5:
                    logger.warning("TXT content too short or empty: %s", asset_slug)
                    stats["skipped"] += 1
                    continue

                # Chunk
                chunks = chunk_text(
                    cleaned,
                    target_tokens=settings.txt_chunk_target_tokens,
                    overlap_tokens=settings.txt_chunk_overlap_tokens,
                )

                # Align to SRT timestamps
                srt_path = find_srt_path_for_txt(asset_slug, conn)
                srt_blocks = parse_srt_file(srt_path) if srt_path else []
                chunks = align_chunks_to_srt(chunks, len(cleaned), srt_blocks)

                # Store
                video_asset_id = find_video_asset_id_for_txt(asset_slug, conn)
                store_txt_transcript(str(asset_id), video_asset_id, chunks, cleaned, conn)

                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE assets SET processing_status = 'processed' WHERE id = %s",
                        (asset_id,),
                    )

                logger.debug(
                    "  %s → %d words, %d chunks, %d srt_blocks",
                    Path(asset_slug).name,
                    count_words(cleaned),
                    len(chunks),
                    len(srt_blocks),
                )
                stats["succeeded"] += 1

            except Exception as exc:
                logger.error("Failed TXT processing %s: %s", asset_slug, exc)
                stats["failed"] += 1

    elapsed_ms = int((time.time() - t0) * 1000)
    logger.info(
        "TXT processing done in %dms — %d ok / %d failed / %d skipped",
        elapsed_ms, stats["succeeded"], stats["failed"], stats["skipped"],
    )
    return stats


if __name__ == "__main__":
    results = process_all_txts()
    sys.exit(0 if results["failed"] == 0 else 1)
