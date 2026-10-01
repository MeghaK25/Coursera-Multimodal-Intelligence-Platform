"""
preprocessing/video/process_videos.py
=======================================
Step 5 — Extract video metadata via ffprobe and create video + segment records.

For each MP4 in data/raw/:
  1. Run ffprobe to extract codec, duration, resolution, fps, audio info.
  2. Validate (has_audio, duration > 0, valid codec).
  3. Create DB record in `videos`.
  4. Segment into 300-second windows (configurable via VIDEO_SEGMENT_SECONDS).
  5. Align SRT captions to each segment window.
  6. Store segments in `video_segments`.

Usage:
    python preprocessing/video/process_videos.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from preprocessing.common.config import settings
from preprocessing.common.db import get_db
from preprocessing.common.logging_utils import get_logger
from preprocessing.common.models import VideoMetadata, SRTBlock
from preprocessing.common.utils import count_tokens
from preprocessing.transcript.process_srt import parse_srt_file

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# ffprobe integration
# ---------------------------------------------------------------------------

def run_ffprobe(video_path: Path) -> Optional[dict]:
    """
    Run ffprobe and return the raw JSON output as a dict.
    Returns None if ffprobe is not available or fails.
    """
    if settings.skip_video_metadata:
        logger.debug("SKIP_VIDEO_METADATA=true — skipping ffprobe for %s", video_path.name)
        return None

    try:
        import ffmpeg  # ffmpeg-python
        probe = ffmpeg.probe(str(video_path))
        return probe
    except Exception as exc:
        logger.warning("ffprobe failed for %s: %s", video_path.name, exc)
        return None


def parse_ffprobe(probe: dict) -> VideoMetadata:
    """Parse ffprobe JSON into a VideoMetadata model."""
    if not probe:
        return VideoMetadata(metadata_raw=None)

    format_info = probe.get("format", {})
    streams = probe.get("streams", [])

    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    duration = None
    if format_info.get("duration"):
        try:
            duration = float(format_info["duration"])
        except ValueError:
            pass

    width = video_stream.get("width") if video_stream else None
    height = video_stream.get("height") if video_stream else None

    frame_rate = None
    if video_stream and video_stream.get("avg_frame_rate"):
        try:
            num, den = video_stream["avg_frame_rate"].split("/")
            if int(den) > 0:
                frame_rate = round(int(num) / int(den), 3)
        except Exception:
            pass

    bit_rate = None
    if format_info.get("bit_rate"):
        try:
            bit_rate = int(format_info["bit_rate"]) // 1000
        except ValueError:
            pass

    return VideoMetadata(
        duration_seconds=duration,
        width_px=width,
        height_px=height,
        frame_rate=frame_rate,
        video_codec=video_stream.get("codec_name") if video_stream else None,
        audio_codec=audio_stream.get("codec_name") if audio_stream else None,
        audio_channels=audio_stream.get("channels") if audio_stream else None,
        audio_sample_rate_hz=int(audio_stream["sample_rate"]) if audio_stream and audio_stream.get("sample_rate") else None,
        has_audio=audio_stream is not None,
        container_format=format_info.get("format_name"),
        bit_rate_kbps=bit_rate,
        metadata_raw=probe,
    )


# ---------------------------------------------------------------------------
# Segmentation
# ---------------------------------------------------------------------------

def create_segments(
    duration_seconds: float,
    window_seconds: int,
    srt_blocks: list[SRTBlock],
) -> list[dict]:
    """
    Divide a video into fixed-size time windows.
    For each window, collect the SRT captions whose start_seconds falls inside.

    Returns a list of segment dicts.
    """
    segments = []
    seg_idx = 0
    t = 0.0

    while t < duration_seconds:
        t_end = min(t + window_seconds, duration_seconds)

        # Collect SRT blocks that overlap this window
        aligned_blocks = [
            b for b in srt_blocks
            if b.start_seconds < t_end and b.end_seconds > t
        ]
        transcript_text = " ".join(b.text for b in aligned_blocks).strip() or None
        token_count = count_tokens(transcript_text) if transcript_text else 0

        segments.append({
            "segment_index":   seg_idx,
            "start_seconds":   round(t, 3),
            "end_seconds":     round(t_end, 3),
            "transcript_text": transcript_text,
            "token_count":     token_count,
        })
        seg_idx += 1
        t = t_end

    return segments


# ---------------------------------------------------------------------------
# DB operations
# ---------------------------------------------------------------------------

def find_companion_srt(video_asset_slug: str, conn) -> Optional[list[SRTBlock]]:
    """
    Find the SRT transcript asset for a given video, load and parse it.
    e.g. '01_01_..mp4' → '01_01_...en.srt'
    """
    # Derive the SRT slug from the video slug (replace .mp4 with .en.srt)
    srt_slug = video_asset_slug.replace(".mp4", ".en.srt")
    with conn.cursor() as cur:
        cur.execute(
            "SELECT extracted_path FROM assets WHERE asset_slug = %s LIMIT 1",
            (srt_slug,),
        )
        row = cur.fetchone()
    if not row or not row[0]:
        return None
    srt_path = Path(row[0])
    if not srt_path.exists():
        return None
    return parse_srt_file(srt_path)


def process_single_video(asset_id: str, asset_slug: str, extracted_path: str, conn) -> bool:
    """Process one video: ffprobe + segmentation → DB insert."""
    video_path = Path(extracted_path)
    if not video_path.exists():
        logger.error("Video file missing: %s", extracted_path)
        return False

    # --- ffprobe ---
    probe = run_ffprobe(video_path)
    meta = parse_ffprobe(probe)

    # --- Validation ---
    if meta.duration_seconds is not None and meta.duration_seconds <= 0:
        logger.warning("Invalid duration (%.2f) for %s", meta.duration_seconds, video_path.name)

    if not meta.has_audio:
        logger.warning("No audio stream detected in %s", video_path.name)

    # --- Insert into videos ---
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO videos (
                id, duration_seconds, width_px, height_px, frame_rate,
                video_codec, audio_codec, audio_channels, audio_sample_rate_hz,
                has_audio, container_format, bit_rate_kbps, metadata_raw, extracted_at
            ) VALUES (
                %(id)s, %(duration_seconds)s, %(width_px)s, %(height_px)s, %(frame_rate)s,
                %(video_codec)s, %(audio_codec)s, %(audio_channels)s, %(audio_sample_rate_hz)s,
                %(has_audio)s, %(container_format)s, %(bit_rate_kbps)s, %(metadata_raw)s, NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                duration_seconds     = EXCLUDED.duration_seconds,
                width_px             = EXCLUDED.width_px,
                height_px            = EXCLUDED.height_px,
                frame_rate           = EXCLUDED.frame_rate,
                video_codec          = EXCLUDED.video_codec,
                audio_codec          = EXCLUDED.audio_codec,
                has_audio            = EXCLUDED.has_audio,
                container_format     = EXCLUDED.container_format,
                bit_rate_kbps        = EXCLUDED.bit_rate_kbps,
                metadata_raw         = EXCLUDED.metadata_raw,
                extracted_at         = NOW()
            """,
            {
                "id": asset_id,
                "duration_seconds": meta.duration_seconds,
                "width_px": meta.width_px,
                "height_px": meta.height_px,
                "frame_rate": meta.frame_rate,
                "video_codec": meta.video_codec,
                "audio_codec": meta.audio_codec,
                "audio_channels": meta.audio_channels,
                "audio_sample_rate_hz": meta.audio_sample_rate_hz,
                "has_audio": meta.has_audio,
                "container_format": meta.container_format,
                "bit_rate_kbps": meta.bit_rate_kbps,
                "metadata_raw": json.dumps(meta.metadata_raw) if meta.metadata_raw else None,
            },
        )

    # --- SRT alignment ---
    duration = meta.duration_seconds or 0.0
    srt_blocks = find_companion_srt(asset_slug, conn) or []
    segments = create_segments(
        duration_seconds=duration,
        window_seconds=settings.video_segment_seconds,
        srt_blocks=srt_blocks,
    )

    if segments:
        # Delete existing segments first (idempotent)
        with conn.cursor() as cur:
            cur.execute("DELETE FROM video_segments WHERE video_id = %s", (asset_id,))

        seg_rows = [
            {
                "video_id":       asset_id,
                "segment_index":  s["segment_index"],
                "start_seconds":  s["start_seconds"],
                "end_seconds":    s["end_seconds"],
                "transcript_text": s["transcript_text"],
                "token_count":    s["token_count"],
            }
            for s in segments
        ]
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO video_segments
                    (video_id, segment_index, start_seconds, end_seconds,
                     transcript_text, token_count)
                VALUES
                    (%(video_id)s, %(segment_index)s, %(start_seconds)s, %(end_seconds)s,
                     %(transcript_text)s, %(token_count)s)
                """,
                seg_rows,
            )

    logger.debug(
        "  %s → duration=%.1fs  segments=%d  srt_blocks=%d",
        video_path.name,
        duration,
        len(segments),
        len(srt_blocks),
    )
    return True


def process_all_videos() -> dict:
    """Process every video asset in the database. Returns summary counters."""
    t0 = time.time()
    stats = {"total": 0, "succeeded": 0, "failed": 0, "skipped": 0}

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, asset_slug, extracted_path
                FROM assets
                WHERE asset_category = 'video'
                  AND processing_status != 'skipped'
                ORDER BY asset_slug
                """
            )
            rows = cur.fetchall()

        logger.info("Processing %d video assets …", len(rows))

        for (asset_id, asset_slug, extracted_path) in rows:
            stats["total"] += 1
            if not extracted_path:
                logger.warning("No extracted_path for asset %s — skipping.", asset_slug)
                stats["skipped"] += 1
                continue
            try:
                ok = process_single_video(str(asset_id), asset_slug, extracted_path, conn)
                if ok:
                    # Update processing_status
                    with conn.cursor() as cur:
                        cur.execute(
                            "UPDATE assets SET processing_status = 'processed' WHERE id = %s",
                            (asset_id,),
                        )
                    stats["succeeded"] += 1
                else:
                    stats["failed"] += 1
            except Exception as exc:
                logger.error("Failed processing video %s: %s", asset_slug, exc)
                stats["failed"] += 1

    elapsed_ms = int((time.time() - t0) * 1000)
    logger.info(
        "Video processing done in %dms — %d ok / %d failed / %d skipped",
        elapsed_ms, stats["succeeded"], stats["failed"], stats["skipped"],
    )
    return stats


if __name__ == "__main__":
    results = process_all_videos()
    sys.exit(0 if results["failed"] == 0 else 1)
