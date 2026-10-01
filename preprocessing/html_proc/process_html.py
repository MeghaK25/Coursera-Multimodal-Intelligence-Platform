"""
preprocessing/html/process_html.py
=====================================
Step 8 — Process HTML reading/instruction files.

For each HTML file:
  1. Parse HTML with BeautifulSoup4.
  2. Detect and extract embedded base64 images → data/processed/images/.
  3. Strip base64 blobs and <co-content> wrappers from text.
  4. Extract clean prose text.
  5. Classify into reading_subtype.
  6. Set rag_enabled based on classification.
  7. Store in readings table.

Usage:
    python preprocessing/html/process_html.py
"""

from __future__ import annotations

import base64
import hashlib
import re
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from bs4 import BeautifulSoup

from preprocessing.common.config import settings
from preprocessing.common.db import get_db
from preprocessing.common.logging_utils import get_logger
from preprocessing.common.utils import normalize_whitespace, count_words
from preprocessing.common.models import ReadingSubtype

logger = get_logger(__name__)

BASE64_IMG_RE = re.compile(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+')
BINARY_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".mp4", ".zip", ".ico"}


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def classify_html(filename: str) -> ReadingSubtype:
    """Infer reading_subtype from filename."""
    lower = filename.lower()
    if "lesson-overview" in lower or "lesson_overview" in lower:
        return ReadingSubtype.LESSON_OVERVIEW
    if "lesson-summary" in lower or "summary" in lower:
        return ReadingSubtype.LESSON_SUMMARY
    if "course-syllabus" in lower or "syllabus" in lower:
        return ReadingSubtype.COURSE_SYLLABUS
    if "helpful-tips" in lower or "helpful_tips" in lower:
        return ReadingSubtype.TIPS
    if "infograph" in lower:
        return ReadingSubtype.INFOGRAPHIC
    if "final-assignment" in lower or "roadmap" in lower:
        return ReadingSubtype.ASSIGNMENT
    if "digital-badge" in lower or "congrats" in lower or "next-steps" in lower \
            or "course-team" in lower or "acknowledgements" in lower:
        return ReadingSubtype.ADMINISTRATIVE
    return ReadingSubtype.OTHER


def rag_for_subtype(subtype: ReadingSubtype) -> bool:
    """Administrative pages are excluded from RAG corpus."""
    return subtype not in {ReadingSubtype.ADMINISTRATIVE}


# ---------------------------------------------------------------------------
# Image extraction
# ---------------------------------------------------------------------------

def extract_base64_images(html_content: str, asset_slug: str) -> tuple[str, Optional[str]]:
    """
    Find and extract base64-encoded images from HTML.
    Saves the extracted PNG/JPG to data/processed/images/.
    Returns (cleaned_html, image_path_or_None).
    """
    matches = BASE64_IMG_RE.findall(html_content)
    if not matches:
        return html_content, None

    images_dir = settings.images_dir
    images_dir.mkdir(parents=True, exist_ok=True)

    first_image_path = None
    cleaned = html_content

    for blob in matches:
        header, data = blob.split(",", 1)
        ext = "png" if "png" in header else "jpg"

        content_hash = hashlib.sha256(data.encode()).hexdigest()[:12]
        slug_stem = Path(asset_slug).stem.replace(" ", "_")[:50]
        img_filename = f"{slug_stem}_{content_hash}.{ext}"
        img_path = images_dir / img_filename

        if not img_path.exists():
            try:
                img_path.write_bytes(base64.b64decode(data))
                logger.debug("Extracted embedded image: %s (%d bytes)", img_path.name, img_path.stat().st_size)
            except Exception as exc:
                logger.warning("Failed to extract base64 image from %s: %s", asset_slug, exc)
                continue

        if first_image_path is None:
            first_image_path = str(img_path)

        cleaned = cleaned.replace(blob, f"extracted://{img_path.name}")

    return cleaned, first_image_path


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text(html) -> str:
    """
    Parse HTML, remove boilerplate, extract clean prose text.
    Handles Coursera's <co-content> custom element.
    """
    if isinstance(html, (bytes, bytearray)):
        html = html.decode("utf-8", errors="replace")

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["script", "style", "head", "noscript"]):
        tag.decompose()

    for co in soup.find_all("co-content"):
        co.unwrap()

    text = soup.get_text(separator=" ", strip=True)
    return normalize_whitespace(text)


# ---------------------------------------------------------------------------
# DB operations
# ---------------------------------------------------------------------------

def store_reading(
    asset_id: str,
    subtype: ReadingSubtype,
    raw_html: str,
    extracted_text: str,
    has_embedded_image: bool,
    embedded_image_path: Optional[str],
    conn,
) -> None:
    # Ensure NUL bytes are completely purged for PostgreSQL text fields
    clean_raw_html = raw_html[:50000].replace("\x00", "")
    clean_extracted_text = extracted_text.replace("\x00", "")

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO readings (
                id, reading_subtype, raw_html, extracted_text,
                has_embedded_image, embedded_image_path,
                char_count, word_count, extracted_at
            ) VALUES (
                %(id)s, %(reading_subtype)s, %(raw_html)s, %(extracted_text)s,
                %(has_embedded_image)s, %(embedded_image_path)s,
                %(char_count)s, %(word_count)s, NOW()
            )
            ON CONFLICT (id) DO UPDATE SET
                reading_subtype     = EXCLUDED.reading_subtype,
                raw_html            = EXCLUDED.raw_html,
                extracted_text      = EXCLUDED.extracted_text,
                has_embedded_image  = EXCLUDED.has_embedded_image,
                embedded_image_path = EXCLUDED.embedded_image_path,
                char_count          = EXCLUDED.char_count,
                word_count          = EXCLUDED.word_count,
                extracted_at        = NOW()
            """,
            {
                "id":                  asset_id,
                "reading_subtype":     subtype.value,
                "raw_html":            clean_raw_html,
                "extracted_text":      clean_extracted_text,
                "has_embedded_image":  has_embedded_image,
                "embedded_image_path": embedded_image_path,
                "char_count":          len(clean_extracted_text),
                "word_count":          count_words(clean_extracted_text),
            },
        )


def process_all_html() -> dict:
    """Process all HTML assets (readings, infographics, assignments, administrative)."""
    t0 = time.time()
    stats = {"total": 0, "succeeded": 0, "failed": 0, "skipped": 0}

    html_categories = ("reading", "infographic", "assignment", "administrative")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id, asset_slug, file_name, extracted_path
                FROM assets
                WHERE asset_category = ANY(ARRAY{list(html_categories)}::asset_category_enum[])
                ORDER BY asset_slug
                """
            )
            rows = cur.fetchall()

        logger.info("Processing %d HTML files …", len(rows))

        for (asset_id, asset_slug, file_name, extracted_path) in rows:
            stats["total"] += 1
            if not extracted_path or not Path(extracted_path).exists():
                logger.warning("HTML file not found: %s", extracted_path)
                stats["skipped"] += 1
                continue

            # Skip binary files that are not HTML/text readings
            ext = Path(file_name).suffix.lower()
            if ext in BINARY_EXTENSIONS:
                logger.debug("Skipping binary non-HTML asset: %s", file_name)
                stats["skipped"] += 1
                continue

            try:
                raw_html = Path(extracted_path).read_text(encoding="utf-8", errors="replace").replace("\x00", "")

                # Detect and extract base64 images
                has_embedded_image = bool(BASE64_IMG_RE.search(raw_html))
                cleaned_html, img_path = extract_base64_images(raw_html, asset_slug)

                # Extract text
                extracted_text = extract_text(cleaned_html).replace("\x00", "")

                # Classify
                subtype = classify_html(file_name)
                rag_on = rag_for_subtype(subtype)

                if not extracted_text or count_words(extracted_text) < 3:
                    logger.warning("Very short/empty extracted text for %s", asset_slug)

                # Store reading record
                store_reading(
                    str(asset_id),
                    subtype,
                    raw_html,
                    extracted_text,
                    has_embedded_image,
                    img_path,
                    conn,
                )

                # Update asset status
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE assets
                        SET processing_status = 'processed',
                            rag_enabled = %s
                        WHERE id = %s
                        """,
                        (rag_on, asset_id),
                    )

                conn.commit()

                logger.debug(
                    "  %s → subtype=%s rag=%s embedded_img=%s words=%d",
                    file_name,
                    subtype.value,
                    rag_on,
                    has_embedded_image,
                    count_words(extracted_text),
                )
                stats["succeeded"] += 1

            except Exception as exc:
                conn.rollback()
                logger.error("Failed HTML processing %s: %s", asset_slug, exc)
                stats["failed"] += 1

    elapsed_ms = int((time.time() - t0) * 1000)
    logger.info(
        "HTML processing done in %dms — %d ok / %d failed / %d skipped",
        elapsed_ms, stats["succeeded"], stats["failed"], stats["skipped"],
    )
    return stats


if __name__ == "__main__":
    results = process_all_html()
    sys.exit(0 if results["failed"] == 0 else 1)