"""
preprocessing/load_to_db.py
=============================
Step 11 — Load course hierarchy and assets from inventory JSON into PostgreSQL.
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.common.config import settings
from preprocessing.common.db import get_db, upsert_returning_id
from preprocessing.common.logging_utils import get_logger
from preprocessing.common.utils import (
    title_from_slug,
    slug_from_path,
    asset_category_from_file,
    rag_enabled_for_category,
    mime_from_extension,
    extract_lesson_prefix,
    extract_module_number,
)

logger = get_logger(__name__)

MODULE_TITLE_MAP = {
    "01_defining-data-science-and-what-data-scientists-do": "Defining Data Science and What Data Scientists Do",
    "02_data-science-topics": "Data Science Topics",
    "03_applications-and-careers-in-data-science": "Applications and Careers in Data Science",
    "04_data-literacy-for-data-science-optional": "Data Literacy for Data Science (Optional)",
}

OPTIONAL_MODULES = {"04_data-literacy-for-data-science-optional"}

def lesson_group_title(group_slug: str) -> str:
    s = re.sub(r'^\d+_', '', group_slug)
    return s.replace("-", " ").title()

def lesson_title_from_slug(lesson_slug: str) -> str:
    s = re.sub(r'^\d{2}_\d{2}_', '', lesson_slug)
    s = re.sub(r'\.(en\.)?(srt|txt|mp4|html)$', '', s, flags=re.IGNORECASE)
    s = re.sub(r'_(instructions|Helpful_Tips_IBM_SkillsNetwork)$', '', s)
    return s.replace("-", " ").replace("_", " ").strip().title()

def lesson_type_from_category(category: str) -> str:
    return {
        "video": "video_lesson",
        "transcript_srt": "video_lesson",
        "transcript_txt": "video_lesson",
        "reading": "reading",
        "infographic": "assignment",
        "assignment": "assignment",
        "administrative": "administrative",
    }.get(category, "reading")

def is_summary(filename: str) -> bool:
    return "lesson-summary" in filename.lower() or "summary" in filename.lower()

def is_overview(filename: str) -> bool:
    return "lesson-overview" in filename.lower()

def load_inventory(inv_path: Path) -> dict:
    if not inv_path.exists():
        logger.error("Inventory file not found: %s", inv_path)
        logger.error("Run preprocessing/extract_course.py first.")
        sys.exit(1)
    with open(inv_path, encoding="utf-8") as f:
        return json.load(f)

def load_course_to_db(inventory: dict) -> dict:
    t0 = time.time()
    stats = {
        "courses": 0, "modules": 0, "lesson_groups": 0,
        "lessons": 0, "assets": 0, "failed": 0,
    }

    assets = inventory.get("assets", [])

    modules: dict[str, dict] = {}
    for asset in assets:
        mod_slug = asset.get("module_slug") or ""
        grp_slug = asset.get("lesson_group_slug") or ""
        filename = asset.get("file_name") or ""
        prefix = asset.get("lesson_prefix") or extract_lesson_prefix(filename)

        if not mod_slug: continue

        if mod_slug not in modules:
            modules[mod_slug] = {
                "module_number": asset.get("module_number") or extract_module_number(mod_slug),
                "is_optional": mod_slug in OPTIONAL_MODULES,
                "groups": {},
            }
        mod = modules[mod_slug]

        if grp_slug and grp_slug not in mod["groups"]:
            mod["groups"][grp_slug] = {
                "group_number": asset.get("group_number") or extract_module_number(grp_slug),
                "lessons": {},
            }

        grp = mod["groups"].get(grp_slug)
        if grp and prefix:
            if prefix not in grp["lessons"]:
                stem = re.sub(r'\.(en\.)?(srt|txt|mp4|html)$', '', filename, flags=re.IGNORECASE)
                stem = re.sub(r'_(instructions|Helpful_Tips_IBM_SkillsNetwork)$', '', stem)
                grp["lessons"][prefix] = {
                    "lesson_slug": stem,
                    "filename": filename,
                }

    with get_db() as conn:
        zip_path = inventory.get("zip_path", "")
        
        # --- DYNAMIC COURSE NAME FIX ---
        dyn_course_slug = inventory.get("course_id", "default-course-slug")
        dyn_course_name = inventory.get("course_name", "Unknown Course")

        course_id = upsert_returning_id(
            conn,
            "courses",
            {
                "course_slug":  dyn_course_slug,
                "course_name":  dyn_course_name,
                "source":       "authorized_local_dataset",
                "zip_path":     zip_path,
                "root_folder":  inventory.get("root_folder", ""),
                "total_assets": len(assets),
            },
            conflict_columns=["course_slug"],
        )
        stats["courses"] = 1
        logger.info("Course loaded: %s (id=%s)", dyn_course_name, course_id[:8])

        # --- DUMMY LESSON FIX ---
        dummy_mod_id = upsert_returning_id(
            conn, "course_modules",
            {"course_id": course_id, "module_slug": "uncategorized_mod", "module_number": 999, "module_title": "Uncategorized", "is_optional": True, "sort_order": 999},
            conflict_columns=["course_id", "module_number"]
        )
        dummy_grp_id = upsert_returning_id(
            conn, "lesson_groups",
            {"module_id": dummy_mod_id, "group_slug": "uncategorized_grp", "group_number": 999, "group_title": "Uncategorized Assets", "sort_order": 999},
            conflict_columns=["module_id", "group_number"]
        )
        dummy_les_id = upsert_returning_id(
            conn, "lessons",
            {"lesson_group_id": dummy_grp_id, "lesson_slug": "uncategorized_les", "lesson_prefix": "999", "lesson_title": "Standalone Files", "lesson_type": "reading", "is_summary": False, "is_overview": False, "sort_order": 999},
            conflict_columns=["lesson_group_id", "lesson_prefix"]
        )

        module_id_map: dict[str, str] = {}
        for sort_idx, (mod_slug, mod_data) in enumerate(sorted(modules.items(), key=lambda x: x[1]["module_number"])):
            title = MODULE_TITLE_MAP.get(mod_slug, lesson_group_title(mod_slug))
            mod_id = upsert_returning_id(
                conn, "course_modules",
                {"course_id": course_id, "module_slug": mod_slug, "module_number": mod_data["module_number"], "module_title": title, "is_optional": mod_data["is_optional"], "sort_order": sort_idx},
                conflict_columns=["course_id", "module_number"]
            )
            module_id_map[mod_slug] = mod_id
            stats["modules"] += 1

        group_id_map: dict[str, str] = {}
        for mod_slug, mod_data in modules.items():
            mod_id = module_id_map[mod_slug]
            for sort_idx, (grp_slug, grp_data) in enumerate(sorted(mod_data["groups"].items(), key=lambda x: x[1]["group_number"])):
                grp_id = upsert_returning_id(
                    conn, "lesson_groups",
                    {"module_id": mod_id, "group_slug": grp_slug, "group_number": grp_data["group_number"], "group_title": lesson_group_title(grp_slug), "sort_order": sort_idx},
                    conflict_columns=["module_id", "group_number"]
                )
                group_id_map[(mod_slug, grp_slug)] = grp_id
                stats["lesson_groups"] += 1

        lesson_id_map: dict[tuple, str] = {}
        for mod_slug, mod_data in modules.items():
            for grp_slug, grp_data in mod_data["groups"].items():
                grp_id = group_id_map.get((mod_slug, grp_slug))
                if not grp_id: continue
                for sort_idx, (prefix, les_data) in enumerate(sorted(grp_data["lessons"].items())):
                    slug = les_data["lesson_slug"]
                    fname = les_data["filename"]
                    category = asset_category_from_file(fname)
                    l_type = lesson_type_from_category(category)

                    les_id = upsert_returning_id(
                        conn, "lessons",
                        {"lesson_group_id": grp_id, "lesson_slug": slug, "lesson_prefix": prefix, "lesson_title": lesson_title_from_slug(slug), "lesson_type": l_type, "is_summary": is_summary(fname), "is_overview": is_overview(fname), "sort_order": sort_idx},
                        conflict_columns=["lesson_group_id", "lesson_prefix"]
                    )
                    lesson_id_map[(mod_slug, grp_slug, prefix)] = les_id
                    stats["lessons"] += 1

        # ---- Assets ----
        for asset in assets:
            mod_slug = asset.get("module_slug") or ""
            grp_slug = asset.get("lesson_group_slug") or ""
            filename = asset.get("file_name") or ""
            prefix = asset.get("lesson_prefix") or extract_lesson_prefix(filename)

            lesson_id = lesson_id_map.get((mod_slug, grp_slug, prefix))
            
            # Use dummy lesson if unmatched
            if not lesson_id:
                lesson_id = dummy_les_id

            ext = f".{asset.get('file_type', '')}"
            category = asset.get("asset_category") or asset_category_from_file(filename)
            rag_on = asset.get("rag_enabled", rag_enabled_for_category(category))

            try:
                upsert_returning_id(
                    conn, "assets",
                    {
                        "lesson_id": lesson_id,
                        "asset_slug": slug_from_path(asset.get("relative_path", "")),
                        "file_name": filename,
                        "file_type": asset.get("file_type", ""),
                        "mime_type": asset.get("mime_type") or mime_from_extension(ext),
                        "asset_category": category,
                        "rag_enabled": bool(rag_on),
                        "size_bytes": asset.get("size_bytes", 0),
                        "zip_compressed_bytes": asset.get("zip_compressed_bytes"),
                        "last_modified_zip": asset.get("last_modified_zip"),
                        "processing_status": "extracted" if asset.get("extracted_path") else "pending",
                        "extracted_path": asset.get("extracted_path"),
                        "checksum_sha256": asset.get("checksum_sha256"),
                    },
                    conflict_columns=["asset_slug"],
                )
                stats["assets"] += 1
                conn.commit() 
            except Exception as exc:
                logger.error("Failed inserting asset %s: %s", asset.get("relative_path"), exc)
                conn.rollback()
                stats["failed"] += 1

    elapsed_ms = int((time.time() - t0) * 1000)
    logger.info(
        "DB load complete in %dms — courses=%d modules=%d groups=%d lessons=%d assets=%d failed=%d",
        elapsed_ms, stats["courses"], stats["modules"], stats["lesson_groups"], stats["lessons"], stats["assets"], stats["failed"],
    )
    return stats

def main() -> int:
    logger.info("Loading inventory into database …")
    inventory = load_inventory(settings.inventory_path)
    stats = load_course_to_db(inventory)
    return 0 if stats["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())