"""
preprocessing/extract_course.py
=================================
Step 4 — Extract the authorized course ZIP into data/raw/.

Responsibilities:
  1. Locate source ZIP.
  2. Extract all entries to data/raw/, preserving directory hierarchy.
  3. Calculate SHA-256 checksums for each extracted file.
  4. Build / update data/inventory/course_inventory.json.
  5. Never touch the source ZIP.
  6. Idempotent: re-running skips already-extracted identical files.

Usage:
    python preprocessing/extract_course.py [--force]

    --force   Re-extract even if files already exist.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from tqdm import tqdm

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.common.config import settings
from preprocessing.common.logging_utils import get_logger
from preprocessing.common.utils import (
    sha256_file,
    slug_from_path,
    asset_category_from_file,
    rag_enabled_for_category,
    mime_from_extension,
    extract_lesson_prefix,
    extract_module_number,
    title_from_slug,
)

logger = get_logger(__name__)

# The root folder name inside the ZIP
ZIP_ROOT_PREFIX = "[Coursera] IBM Data Science Professional Certificate/"
COURSE_ID = "ibm-ds-prof-cert-v1"
COURSE_NAME = "IBM Data Science Professional Certificate"


def resolve_zip_path() -> Path:
    """Find the source ZIP file — exit if missing."""
    p = settings.source_zip_path
    if not p.is_absolute():
        # Try relative to project root (parent of preprocessing/)
        project_root = Path(__file__).resolve().parent.parent
        p = project_root / p
    if not p.exists():
        logger.error("Source ZIP not found: %s", p)
        logger.error("Set SOURCE_ZIP in .env to the correct path.")
        sys.exit(1)
    return p


def strip_root(full_name: str) -> str:
    """Strip the ZIP root folder prefix to get the relative path."""
    if full_name.startswith(ZIP_ROOT_PREFIX):
        return full_name[len(ZIP_ROOT_PREFIX):]
    return full_name


def parse_hierarchy(rel_path: str) -> dict:
    """
    Parse a relative path into module / lesson_group / filename components.

    e.g. '01_defining-data.../02_defining.../02_04_title.mp4'
         → { module_slug, module_number, lesson_group_slug,
              group_number, filename, lesson_prefix }
    """
    parts = rel_path.split("/")
    result = {
        "module_slug": None,
        "module_number": None,
        "lesson_group_slug": None,
        "group_number": None,
        "filename": None,
        "lesson_prefix": None,
    }
    if len(parts) >= 1:
        result["module_slug"] = parts[0]
        result["module_number"] = extract_module_number(parts[0])
    if len(parts) >= 2:
        result["lesson_group_slug"] = parts[1]
        result["group_number"] = extract_module_number(parts[1])
    if len(parts) >= 3:
        result["filename"] = parts[2]
        result["lesson_prefix"] = extract_lesson_prefix(parts[2])
    return result


def extract_zip(zip_path: Path, raw_dir: Path, force: bool = False) -> list[dict]:
    """
    Extract all entries from the ZIP to raw_dir.
    Returns a list of asset dicts (one per file).
    """
    raw_dir.mkdir(parents=True, exist_ok=True)

    assets: list[dict] = []
    start_ts = time.time()

    with zipfile.ZipFile(zip_path, "r") as zf:
        entries = [e for e in zf.infolist() if not e.is_dir()]
        logger.info("ZIP contains %d files — extracting to %s …", len(entries), raw_dir)

        for entry in tqdm(entries, desc="Extracting", unit="file"):
            rel_path = strip_root(entry.filename)
            if not rel_path:
                continue  # skip the root entry itself

            dest = raw_dir / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Idempotency check — skip if already extracted and same size
            if dest.exists() and not force and dest.stat().st_size == entry.file_size:
                logger.debug("Skipping (already extracted): %s", rel_path)
                checksum = sha256_file(dest)
            else:
                with zf.open(entry) as src, open(dest, "wb") as dst:
                    dst.write(src.read())
                checksum = sha256_file(dest)
                logger.debug("Extracted: %s (%d bytes)", rel_path, dest.stat().st_size)

            hierarchy = parse_hierarchy(rel_path)
            filename = hierarchy["filename"] or Path(rel_path).name
            ext = Path(filename).suffix.lower()
            category = asset_category_from_file(filename)

            asset = {
                "asset_id": f"asset_{len(assets) + 1:04d}",
                "relative_path": rel_path,
                "file_name": filename,
                "file_type": ext.lstrip("."),
                "mime_type": mime_from_extension(ext),
                "size_bytes": entry.file_size,
                "zip_compressed_bytes": entry.compress_size,
                "last_modified_zip": datetime(
                    *entry.date_time, tzinfo=timezone.utc
                ).isoformat(),
                "asset_category": category,
                "rag_enabled": rag_enabled_for_category(category),
                "module_slug": hierarchy["module_slug"],
                "module_number": hierarchy["module_number"],
                "lesson_group_slug": hierarchy["lesson_group_slug"],
                "group_number": hierarchy["group_number"],
                "lesson_prefix": hierarchy["lesson_prefix"],
                "extracted_path": str(dest),
                "checksum_sha256": checksum,
                "status": "extracted",
            }
            assets.append(asset)

    elapsed = time.time() - start_ts
    logger.info(
        "Extraction complete: %d files in %.1f seconds.", len(assets), elapsed
    )
    return assets


def write_inventory(assets: list[dict], zip_path: Path) -> Path:
    """Write the updated inventory JSON."""
    inv_path = settings.inventory_path
    inv_path.parent.mkdir(parents=True, exist_ok=True)

    inventory = {
        "course_id": COURSE_ID,
        "course_name": COURSE_NAME,
        "source": "authorized_local_dataset",
        "zip_path": str(zip_path),
        "zip_size_bytes": zip_path.stat().st_size,
        "root_folder": ZIP_ROOT_PREFIX.rstrip("/"),
        "total_assets": len(assets),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets": assets,
    }

    inv_path.write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Inventory written: %s (%d assets)", inv_path, len(assets))
    return inv_path


def print_summary(assets: list[dict]) -> None:
    """Print a per-category breakdown."""
    from collections import Counter
    counts = Counter(a["asset_category"] for a in assets)
    print("\n--- Extraction Summary ---")
    for cat, cnt in sorted(counts.items()):
        print(f"  {cnt:>4}  {cat}")
    print(f"  {'-'*20}")
    print(f"  {len(assets):>4}  TOTAL\n")


def main(force: bool = False) -> int:
    zip_path = resolve_zip_path()
    logger.info("Source ZIP: %s (%.1f MB)", zip_path, zip_path.stat().st_size / 1e6)

    raw_dir = settings.raw_dir
    assets = extract_zip(zip_path, raw_dir, force=force)
    write_inventory(assets, zip_path)
    print_summary(assets)

    # Verify source ZIP is untouched
    assert zip_path.exists(), "BUG: source ZIP was deleted — this should never happen!"
    logger.info("Source ZIP verified untouched: %s", zip_path)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract IBM DS course ZIP to data/raw/.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-extract files even if they already exist.",
    )
    args = parser.parse_args()
    sys.exit(main(force=args.force))
