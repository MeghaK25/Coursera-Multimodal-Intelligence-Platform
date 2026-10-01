"""
database/validate_phase3.py
============================
Comprehensive Phase 3 validation queries.
Runs all checks and prints structured results for the Phase 3 report.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from preprocessing.common.db import get_db

def run_validation():
    results = {}

    with get_db() as conn:
        def q(label, sql, params=None):
            with conn.cursor() as cur:
                cur.execute(sql, params or [])
                return cur.fetchall()

        def q1(sql, params=None):
            with conn.cursor() as cur:
                cur.execute(sql, params or [])
                row = cur.fetchone()
                return row[0] if row else None

        # ── Section 1: Record Counts ──────────────────────────────────────────
        tables = ["courses","course_modules","lesson_groups","lessons","assets",
                  "videos","video_segments","transcripts","transcript_segments",
                  "readings","processing_jobs","data_quality_issues"]
        counts = {}
        for t in tables:
            counts[t] = q1(f"SELECT COUNT(*) FROM {t}")
        results["record_counts"] = counts
        print("\n=== RECORD COUNTS ===")
        for t, c in counts.items():
            print(f"  {t:<30} {c:>6}")

        # ── Section 2: Assets by Category ─────────────────────────────────────
        rows = q("assets_by_category",
                 "SELECT asset_category, COUNT(*) FROM assets GROUP BY asset_category ORDER BY asset_category")
        results["assets_by_category"] = {r[0]: r[1] for r in rows}
        print("\n=== ASSETS BY CATEGORY ===")
        for r in rows: print(f"  {r[0]:<20} {r[1]:>4}")

        # ── Section 3: Assets by Status ───────────────────────────────────────
        rows = q("assets_by_status",
                 "SELECT processing_status, COUNT(*) FROM assets GROUP BY processing_status ORDER BY processing_status")
        results["assets_by_status"] = {r[0]: r[1] for r in rows}
        print("\n=== ASSETS BY PROCESSING STATUS ===")
        for r in rows: print(f"  {r[0]:<20} {r[1]:>4}")

        # ── Section 4: RAG enabled ─────────────────────────────────────────────
        rows = q("rag_enabled",
                 "SELECT rag_enabled, COUNT(*) FROM assets GROUP BY rag_enabled ORDER BY rag_enabled")
        results["rag_enabled"] = {str(r[0]): r[1] for r in rows}
        print("\n=== RAG ENABLED ===")
        for r in rows: print(f"  rag_enabled={r[0]:<5}  {r[1]:>4}")

        # ── Section 5: Modules ────────────────────────────────────────────────
        rows = q("modules",
                 """SELECT module_number, module_title, is_optional,
                    (SELECT COUNT(*) FROM lesson_groups WHERE module_id=cm.id) AS groups
                    FROM course_modules cm ORDER BY module_number""")
        results["modules"] = [{"num":r[0],"title":r[1],"optional":r[2],"groups":r[3]} for r in rows]
        print("\n=== MODULES ===")
        for r in rows:
            print(f"  Module {r[0]:02d}: {r[1]:<55} optional={r[2]}  groups={r[3]}")

        # ── Section 6: Lesson Groups per Module ───────────────────────────────
        rows = q("lesson_groups",
                 """SELECT cm.module_number, lg.group_number, lg.group_title,
                    COUNT(l.id) as lessons
                    FROM lesson_groups lg
                    JOIN course_modules cm ON cm.id=lg.module_id
                    LEFT JOIN lessons l ON l.lesson_group_id=lg.id
                    GROUP BY cm.module_number, lg.group_number, lg.group_title
                    ORDER BY cm.module_number, lg.group_number""")
        results["lesson_groups"] = [{"mod":r[0],"grp":r[1],"title":r[2],"lessons":r[3]} for r in rows]
        print("\n=== LESSON GROUPS ===")
        for r in rows:
            print(f"  M{r[0]:02d}/G{r[1]:02d}: {r[2]:<50} lessons={r[3]}")

        # ── Section 7: SRT Validation ─────────────────────────────────────────
        srt_total = q1("SELECT COUNT(*) FROM transcripts WHERE source_format='srt'")
        srt_segs  = q1("SELECT COUNT(*) FROM transcript_segments WHERE chunk_type='srt_caption'")
        srt_empty = q1("SELECT COUNT(*) FROM transcript_segments WHERE chunk_type='srt_caption' AND (text IS NULL OR TRIM(text)='')")
        srt_bad_ts = q1("SELECT COUNT(*) FROM transcript_segments WHERE chunk_type='srt_caption' AND end_time_seconds < start_time_seconds")
        srt_no_ts  = q1("SELECT COUNT(*) FROM transcript_segments WHERE chunk_type='srt_caption' AND start_time_seconds IS NULL")
        srt_conf   = q("srt_confidence",
                       "SELECT timestamp_confidence, COUNT(*) FROM transcript_segments WHERE chunk_type='srt_caption' GROUP BY timestamp_confidence")
        results["srt"] = {"total":srt_total,"segments":srt_segs,"empty":srt_empty,
                          "bad_timestamps":srt_bad_ts,"no_timestamp":srt_no_ts,
                          "confidence":{r[0]:r[1] for r in srt_conf}}
        print(f"\n=== SRT VALIDATION ===")
        print(f"  Total SRT transcripts : {srt_total}")
        print(f"  Total SRT segments    : {srt_segs}")
        print(f"  Empty captions        : {srt_empty}")
        print(f"  Bad timestamps        : {srt_bad_ts}")
        print(f"  No timestamp          : {srt_no_ts}")
        for r in srt_conf:
            print(f"  confidence={r[0]:<6}    {r[1]:>6}")

        # ── Section 8: TXT Validation ─────────────────────────────────────────
        txt_total  = q1("SELECT COUNT(*) FROM transcripts WHERE source_format='txt'")
        txt_chunks = q1("SELECT COUNT(*) FROM transcript_segments WHERE chunk_type='txt_window'")
        txt_min    = q1("SELECT MIN(token_count) FROM transcript_segments WHERE chunk_type='txt_window'")
        txt_max    = q1("SELECT MAX(token_count) FROM transcript_segments WHERE chunk_type='txt_window'")
        txt_avg    = q1("SELECT ROUND(AVG(token_count)) FROM transcript_segments WHERE chunk_type='txt_window'")
        txt_ts_aligned = q1("SELECT COUNT(*) FROM transcript_segments WHERE chunk_type='txt_window' AND start_time_seconds IS NOT NULL")
        txt_no_ts      = q1("SELECT COUNT(*) FROM transcript_segments WHERE chunk_type='txt_window' AND start_time_seconds IS NULL")
        results["txt"] = {"total":txt_total,"chunks":txt_chunks,"min_tokens":txt_min,
                          "max_tokens":txt_max,"avg_tokens":int(txt_avg or 0),
                          "timestamp_aligned":txt_ts_aligned,"no_timestamp":txt_no_ts}
        print(f"\n=== TXT VALIDATION ===")
        print(f"  Total TXT transcripts : {txt_total}")
        print(f"  Total chunks          : {txt_chunks}")
        print(f"  Token range           : {txt_min} – {txt_max}  (avg {txt_avg})")
        print(f"  Timestamp-aligned     : {txt_ts_aligned}")
        print(f"  No timestamp          : {txt_no_ts}")

        # ── Section 9: HTML / Readings Validation ─────────────────────────────
        html_total   = q1("SELECT COUNT(*) FROM readings")
        html_subtypes = q("html_subtypes",
                          "SELECT reading_subtype, COUNT(*) FROM readings GROUP BY reading_subtype ORDER BY reading_subtype")
        html_rag = q("html_rag",
                     """SELECT a.rag_enabled, COUNT(*) FROM readings r
                        JOIN assets a ON a.id=r.id GROUP BY a.rag_enabled""")
        html_embedded = q1("SELECT COUNT(*) FROM readings WHERE has_embedded_image=true")
        results["html"] = {"total":html_total,
                           "subtypes":{r[0]:r[1] for r in html_subtypes},
                           "rag":{str(r[0]):r[1] for r in html_rag},
                           "embedded_images":html_embedded}
        print(f"\n=== HTML VALIDATION ===")
        print(f"  Total readings        : {html_total}")
        print(f"  With embedded image   : {html_embedded}")
        for r in html_subtypes:
            print(f"  {r[0]:<25} {r[1]:>4}")
        for r in html_rag:
            print(f"  rag_enabled={r[0]}    {r[1]:>4}")

        # ── Section 10: Orphan checks ─────────────────────────────────────────
        orphan_assets   = q1("SELECT COUNT(*) FROM assets WHERE lesson_id IS NULL")
        orphan_lessons  = q1("SELECT COUNT(*) FROM lessons WHERE lesson_group_id IS NULL")
        orphan_groups   = q1("SELECT COUNT(*) FROM lesson_groups WHERE module_id IS NULL")
        orphan_modules  = q1("SELECT COUNT(*) FROM course_modules WHERE course_id IS NULL")
        orphan_videos   = q1("SELECT COUNT(*) FROM videos WHERE id NOT IN (SELECT id FROM assets)")
        orphan_trans    = q1("SELECT COUNT(*) FROM transcripts WHERE id NOT IN (SELECT id FROM assets)")
        orphan_readings = q1("SELECT COUNT(*) FROM readings WHERE id NOT IN (SELECT id FROM assets)")
        orphan_segs     = q1("SELECT COUNT(*) FROM transcript_segments WHERE transcript_id NOT IN (SELECT id FROM transcripts)")
        results["orphans"] = {
            "assets":orphan_assets,"lessons":orphan_lessons,
            "lesson_groups":orphan_groups,"modules":orphan_modules,
            "videos":orphan_videos,"transcripts":orphan_trans,
            "readings":orphan_readings,"transcript_segments":orphan_segs
        }
        print(f"\n=== ORPHAN CHECK (all should be 0) ===")
        for k, v in results["orphans"].items():
            status = "OK" if v == 0 else "PROBLEM!"
            print(f"  orphan_{k:<22} {v:>4}  [{status}]")

        # ── Section 11: Duplicate assets check ────────────────────────────────
        dup_slugs  = q1("SELECT COUNT(*) FROM (SELECT asset_slug FROM assets GROUP BY asset_slug HAVING COUNT(*)>1) x")
        dup_checksums = q1("SELECT COUNT(*) FROM (SELECT checksum_sha256 FROM assets WHERE checksum_sha256 IS NOT NULL GROUP BY checksum_sha256 HAVING COUNT(*)>1) x")
        results["duplicates"] = {"duplicate_slugs":dup_slugs,"duplicate_checksums":dup_checksums}
        print(f"\n=== DUPLICATE CHECK ===")
        print(f"  Duplicate asset_slugs : {dup_slugs}  [{'OK' if dup_slugs==0 else 'PROBLEM!'}]")
        print(f"  Duplicate checksums   : {dup_checksums}")

        # ── Section 12: Processing jobs ───────────────────────────────────────
        jobs = q("jobs","SELECT status, COUNT(*) FROM processing_jobs GROUP BY status")
        results["processing_jobs"] = {r[0]:r[1] for r in jobs}
        print(f"\n=== PROCESSING JOBS ===")
        if not jobs:
            print("  (no processing_jobs records — jobs not tracked in this pipeline version)")
        for r in jobs:
            print(f"  {r[0]:<20} {r[1]:>4}")

        # ── Section 13: DQ Issues ─────────────────────────────────────────────
        dq_rows = q("dq","SELECT issue_code, severity, category, description, asset_id FROM data_quality_issues ORDER BY severity, issue_code")
        results["dq_issues"] = [{"code":r[0],"severity":r[1],"category":r[2],"desc":r[3],"asset_id":str(r[4]) if r[4] else None} for r in dq_rows]
        print(f"\n=== DATA QUALITY ISSUES ({len(dq_rows)} total) ===")
        for r in dq_rows[:30]:
            print(f"  [{r[1].upper():6}] {r[0]}  {r[2]:<15}  {r[3][:60]}")

        # ── Section 14: Sample Lineage ─────────────────────────────────────────
        lineage = q("lineage",
                    """SELECT c.course_name, cm.module_number, cm.module_title, lg.group_title,
                              l.lesson_title, a.file_name, a.asset_category, a.rag_enabled,
                              a.checksum_sha256, a.asset_slug
                       FROM assets a
                       JOIN lessons l ON l.id=a.lesson_id
                       JOIN lesson_groups lg ON lg.id=l.lesson_group_id
                       JOIN course_modules cm ON cm.id=lg.module_id
                       JOIN courses c ON c.id=cm.course_id
                       WHERE a.asset_category = 'transcript_srt'
                       ORDER BY a.asset_slug
                       LIMIT 3""")
        results["sample_lineage"] = [{"course":r[0],"module":r[1],"module_title":r[2],
                                       "group":r[3],"lesson":r[4],"file":r[5],
                                       "category":r[6],"rag":r[7],
                                       "checksum":r[8][:12]+"..." if r[8] else None,
                                       "slug":r[9]} for r in lineage]
        print(f"\n=== SAMPLE DATA LINEAGE (SRT assets) ===")
        for r in lineage:
            print(f"  Course: {r[0]}")
            print(f"    Module {r[1]}: {r[2]}")
            print(f"    Group: {r[3]}")
            print(f"    Lesson: {r[4]}")
            print(f"    File: {r[5]}  cat={r[6]}  rag={r[7]}")
            print(f"    checksum: {r[8][:16] if r[8] else 'MISSING'}...")
            print()

        # ── Section 15: RAG-excluded assets ───────────────────────────────────
        rag_off = q("rag_off",
                    """SELECT a.asset_slug, a.asset_category, a.file_name
                       FROM assets a WHERE a.rag_enabled=false ORDER BY a.asset_slug""")
        results["rag_excluded"] = [{"slug":r[0],"cat":r[1],"file":r[2]} for r in rag_off]
        print(f"\n=== RAG-EXCLUDED ASSETS (rag_enabled=false) ===")
        for r in rag_off:
            print(f"  [{r[1]:<15}] {r[2]}")

        # ── Section 16: Sample TXT chunk with lineage ──────────────────────────
        sample_chunk = q("sample_chunk",
                         """SELECT ts.segment_index, ts.text, ts.token_count,
                                   ts.start_time_seconds, ts.end_time_seconds, ts.timestamp_confidence,
                                   a.asset_slug, a.file_name
                            FROM transcript_segments ts
                            JOIN transcripts t ON t.id=ts.transcript_id
                            JOIN assets a ON a.id=t.id
                            WHERE ts.chunk_type='txt_window'
                            ORDER BY a.asset_slug, ts.segment_index
                            LIMIT 1""")
        if sample_chunk:
            r = sample_chunk[0]
            results["sample_txt_chunk"] = {
                "file": r[7], "slug": r[6], "segment_index": r[0],
                "token_count": r[2], "text_preview": r[1][:200],
                "start_seconds": float(r[3]) if r[3] else None,
                "end_seconds": float(r[4]) if r[4] else None,
                "confidence": r[5]
            }
            print(f"\n=== SAMPLE TXT CHUNK ===")
            print(f"  File: {r[7]}")
            print(f"  Segment index: {r[0]}  tokens: {r[2]}")
            print(f"  Timestamps: {r[3]} → {r[4]} ({r[5]})")
            print(f"  Text: {r[1][:150]}...")

        # ── Save JSON ──────────────────────────────────────────────────────────
        out = Path("docs/phase3_raw_validation.json")
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
        print(f"\n[saved to {out}]")
        return results

if __name__ == "__main__":
    run_validation()
