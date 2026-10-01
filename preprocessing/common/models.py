"""
preprocessing/common/models.py
================================
Pydantic models used throughout the pipeline for validated data exchange.
These are NOT the ORM models — they are transfer objects for pipeline steps.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums (mirror the DB enums)
# ---------------------------------------------------------------------------

class ProcessingStatus(str, Enum):
    PENDING    = "pending"
    EXTRACTED  = "extracted"
    PROCESSED  = "processed"
    FAILED     = "failed"
    SKIPPED    = "skipped"


class AssetCategory(str, Enum):
    VIDEO         = "video"
    TRANSCRIPT_SRT = "transcript_srt"
    TRANSCRIPT_TXT = "transcript_txt"
    READING       = "reading"
    INFOGRAPHIC   = "infographic"
    ASSIGNMENT    = "assignment"
    ADMINISTRATIVE = "administrative"


class LessonType(str, Enum):
    VIDEO_LESSON = "video_lesson"
    READING      = "reading"
    ASSIGNMENT   = "assignment"
    ADMINISTRATIVE = "administrative"


class ChunkType(str, Enum):
    SRT_CAPTION    = "srt_caption"
    TXT_PARAGRAPH  = "txt_paragraph"
    TXT_WINDOW     = "txt_window"


class TimestampConfidence(str, Enum):
    HIGH = "high"
    LOW  = "low"
    NONE = "none"


class ReadingSubtype(str, Enum):
    LESSON_OVERVIEW = "lesson_overview"
    LESSON_SUMMARY  = "lesson_summary"
    COURSE_SYLLABUS = "course_syllabus"
    ASSIGNMENT      = "assignment"
    INFOGRAPHIC     = "infographic"
    ADMINISTRATIVE  = "administrative"
    TIPS            = "tips"
    OTHER           = "other"


class DQSeverity(str, Enum):
    INFO   = "info"
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


class JobStatus(str, Enum):
    PENDING    = "pending"
    RUNNING    = "running"
    COMPLETED  = "completed"
    FAILED     = "failed"


# ---------------------------------------------------------------------------
# Core data models
# ---------------------------------------------------------------------------

class ZipEntry(BaseModel):
    """Represents one entry from the source ZIP archive."""
    full_name:         str
    size_bytes:        int
    compressed_bytes:  int
    last_write_time:   str

    # Derived fields (populated after parsing)
    module_slug:       Optional[str] = None
    lesson_group_slug: Optional[str] = None
    filename:          Optional[str] = None
    file_type:         Optional[str] = None
    asset_category:    Optional[str] = None
    rag_enabled:       bool = True
    lesson_prefix:     Optional[str] = None


class SRTBlock(BaseModel):
    """One parsed SubRip caption block."""
    sequence_number: int
    start_seconds:   float
    end_seconds:     float
    text:            str

    @field_validator("end_seconds")
    @classmethod
    def end_after_start(cls, v: float, info) -> float:
        start = info.data.get("start_seconds", 0)
        if v < start:
            raise ValueError(f"end_seconds ({v}) must be >= start_seconds ({start})")
        return v


class TranscriptChunk(BaseModel):
    """A processed text segment ready for storage."""
    segment_index:        int
    text:                 str
    chunk_type:           ChunkType
    start_char:           Optional[int] = None
    end_char:             Optional[int] = None
    start_time_seconds:   Optional[float] = None
    end_time_seconds:     Optional[float] = None
    timestamp_confidence: TimestampConfidence = TimestampConfidence.NONE
    srt_sequence_number:  Optional[int] = None
    token_count:          int = 0


class VideoMetadata(BaseModel):
    """ffprobe-extracted video metadata."""
    duration_seconds:     Optional[float] = None
    width_px:             Optional[int] = None
    height_px:            Optional[int] = None
    frame_rate:           Optional[float] = None
    video_codec:          Optional[str] = None
    audio_codec:          Optional[str] = None
    audio_channels:       Optional[int] = None
    audio_sample_rate_hz: Optional[int] = None
    has_audio:            bool = True
    container_format:     Optional[str] = None
    bit_rate_kbps:        Optional[int] = None
    metadata_raw:         Optional[dict] = None


class DQIssue(BaseModel):
    """A data quality issue to record."""
    issue_code:     str
    asset_slug:     Optional[str] = None  # None = course-level
    severity:       DQSeverity
    category:       str
    description:    str
    recommendation: Optional[str] = None


class PipelineResult(BaseModel):
    """Summary result of a pipeline stage."""
    stage:          str
    total:          int = 0
    succeeded:      int = 0
    failed:         int = 0
    skipped:        int = 0
    errors:         list[str] = Field(default_factory=list)
    duration_ms:    int = 0
