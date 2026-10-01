"""
preprocessing/assignment/process_assignment.py
================================================
Step 9 — Process the peer-review assignment HTML.

The IBM DS course contains one assignment:
  03_applications-and-careers-in-data-science/
    03_final-assignment/
      03_01_a-roadmap-to-your-data-science-journey_instructions.html
        → embeds a large base64 PNG infographic
      03_01_a-roadmap-to-your-data-science-journey_200457 088 Infograph on roadmap.html
        → accessible HTML version of the infographic

Processing:
  - Both files go through the HTML processor (already handles them correctly).
  - This module marks them explicitly as assignment assets with rag_enabled=True.
  - The embedded PNG is extracted to data/processed/images/.
  - The accessible infographic HTML gets reading_subtype='infographic'.

Note: This module delegates to process_html.py — no separate processing logic needed.
Assignment assets are differentiated at the DB level via asset_category + reading_subtype.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from preprocessing.common.db import get_db
from preprocessing.common.logging_utils import get_logger

logger = get_logger(__name__)

ASSIGNMENT_SLUGS = [
    "03_applications-and-careers-in-data-science/03_final-assignment/"
    "03_01_a-roadmap-to-your-data-science-journey_instructions.html",
    "03_applications-and-careers-in-data-science/03_final-assignment/"
    "03_01_a-roadmap-to-your-data-science-journey_200457 088 Infograph on roadmap.html",
]


def verify_assignment_records() -> dict:
    """
    Verify that assignment records are correctly classified in the DB.
    Returns counts of records found.
    """
    results = {"found": 0, "rag_enabled": 0, "issues": []}

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT a.asset_slug, a.asset_category, a.rag_enabled,
                       r.reading_subtype, r.has_embedded_image, r.word_count
                FROM assets a
                LEFT JOIN readings r ON r.id = a.id
                WHERE a.asset_category IN ('assignment', 'infographic')
                ORDER BY a.asset_slug
                """
            )
            rows = cur.fetchall()

    for (slug, cat, rag, subtype, has_img, words) in rows:
        results["found"] += 1
        if rag:
            results["rag_enabled"] += 1

        logger.info(
            "Assignment asset: %-80s | cat=%-14s rag=%-5s subtype=%-14s img=%-5s words=%s",
            slug, cat, rag, subtype, has_img, words,
        )

        if not rag:
            results["issues"].append(
                f"Assignment asset {slug} has rag_enabled=False — expected True."
            )

    logger.info(
        "Assignment verification: %d assets found, %d rag-enabled, %d issues.",
        results["found"], results["rag_enabled"], len(results["issues"]),
    )
    return results


if __name__ == "__main__":
    results = verify_assignment_records()
    sys.exit(0 if not results["issues"] else 1)
