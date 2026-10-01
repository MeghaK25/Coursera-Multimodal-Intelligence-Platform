"""
preprocessing/common/utils.py
==============================
Shared utility functions used across the preprocessing pipeline.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from pathlib import Path


# ---------------------------------------------------------------------------
# Checksum
# ---------------------------------------------------------------------------

def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """Return the SHA-256 hex digest of a file. Reads in chunks to handle large files."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Return SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Slug helpers
# ---------------------------------------------------------------------------

def slug_from_path(rel_path: str) -> str:
    """
    Normalise a relative path to a stable, lowercase, slash-separated slug.
    Used as the primary key for deduplication.
    """
    return rel_path.replace("\\", "/").strip("/")


def title_from_slug(slug: str) -> str:
    """
    Convert a filename slug to a human-readable title.
    e.g. '02_02_what-is-data-science' → 'What Is Data Science'
    """
    # Strip numeric prefixes like '02_02_'
    s = re.sub(r'^\d{2}_\d{2}_', '', slug)
    # Replace hyphens and underscores with spaces
    s = s.replace("-", " ").replace("_", " ")
    # Strip extension
    s = re.sub(r'\.\w+$', '', s)
    # Title-case
    return s.strip().title()


def extract_lesson_prefix(filename: str) -> str:
    """
    Extract the NN_NN prefix from a filename.
    e.g. '02_04_what-is-data-science.mp4' → '02_04'
    Returns '' if no prefix found.
    """
    m = re.match(r'^(\d{2}_\d{2})', filename)
    return m.group(1) if m else ""


def extract_module_number(folder_slug: str) -> int:
    """
    Extract the leading module number from a folder slug.
    e.g. '01_defining-data-science-...' → 1
    """
    m = re.match(r'^(\d+)', folder_slug)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------

def normalize_whitespace(text: str) -> str:
    """Collapse multiple whitespace characters into a single space and strip."""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r'\r\n|\r', '\n', text)   # normalize line endings
    text = re.sub(r'[ \t]+', ' ', text)      # collapse horizontal whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)  # max 2 consecutive newlines
    return text.strip()


def count_words(text: str) -> int:
    """Count whitespace-separated tokens as a proxy for words."""
    return len(text.split())


# ---------------------------------------------------------------------------
# MIME types
# ---------------------------------------------------------------------------

MIME_MAP = {
    ".mp4":  "video/mp4",
    ".srt":  "text/srt",
    ".txt":  "text/plain",
    ".html": "text/html",
    ".htm":  "text/html",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
}


def mime_from_extension(ext: str) -> str:
    """Return MIME type for a file extension (with leading dot)."""
    return MIME_MAP.get(ext.lower(), "application/octet-stream")


# ---------------------------------------------------------------------------
# Asset category helpers
# ---------------------------------------------------------------------------

def asset_category_from_file(filename: str) -> str:
    """
    Infer asset_category from filename and extension.
    Returns one of: video, transcript_srt, transcript_txt, reading,
                    infographic, assignment, administrative
    """
    lower = filename.lower()
    ext = Path(filename).suffix.lower()

    if ext == ".mp4":
        return "video"
    if ext == ".srt":
        return "transcript_srt"
    if ext == ".txt":
        return "transcript_txt"
    if ext == ".html":
        if "infograph" in lower:
            return "infographic"
        if "digital-badge" in lower:
            return "administrative"
        if "congrats" in lower or "next-steps" in lower:
            return "administrative"
        if "course-team" in lower or "acknowledgements" in lower:
            return "administrative"
        if "final-assignment" in lower or "roadmap" in lower:
            return "assignment"
        return "reading"
    return "reading"


def rag_enabled_for_category(category: str) -> bool:
    """Return False for administrative assets, True for learning content."""
    return category not in {"administrative"}


# ---------------------------------------------------------------------------
# Token counting (using tiktoken cl100k_base — no API key needed)
# ---------------------------------------------------------------------------

_ENCODER = None


def count_tokens(text: str) -> int:
    """Approximate token count using tiktoken cl100k_base encoding."""
    global _ENCODER
    if _ENCODER is None:
        try:
            import tiktoken
            _ENCODER = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # Fallback: rough approximation
            return len(text.split())
    return len(_ENCODER.encode(text))
