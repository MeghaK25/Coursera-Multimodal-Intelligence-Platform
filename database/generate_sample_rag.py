"""
database/generate_sample_rag.py
================================
Generate sample_rag_records.json from actual database data.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from preprocessing.common.db import get_db

records = []

with get_db() as conn:
    # 2 SRT caption segments with full lineage
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, cm.id, lg.id, l.id, a.id,
                   ts.chunk_type, ts.text, a.extracted_path, a.file_name,
                   ts.start_time_seconds, ts.end_time_seconds,
                   a.rag_enabled, ts.timestamp_confidence, ts.token_count,
                   ts.segment_index
            FROM transcript_segments ts
            JOIN transcripts t ON t.id = ts.transcript_id
            JOIN assets a ON a.id = t.id
            JOIN lessons l ON l.id = a.lesson_id
            JOIN lesson_groups lg ON lg.id = l.lesson_group_id
            JOIN course_modules cm ON cm.id = lg.module_id
            JOIN courses c ON c.id = cm.course_id
            WHERE ts.chunk_type = 'srt_caption'
              AND ts.segment_index BETWEEN 1 AND 2
            ORDER BY a.asset_slug, ts.segment_index
            LIMIT 2
        """)
        for r in cur.fetchall():
            records.append({
                "course_id": str(r[0]),
                "module_id": str(r[1]),
                "lesson_group_id": str(r[2]),
                "lesson_id": str(r[3]),
                "asset_id": str(r[4]),
                "modality": "transcript_srt",
                "chunk_type": r[5],
                "content": r[6],
                "source_file": r[8],
                "source_path": r[7],
                "start_time_seconds": float(r[9]) if r[9] else None,
                "end_time_seconds": float(r[10]) if r[10] else None,
                "rag_enabled": bool(r[11]),
                "timestamp_confidence": r[12],
                "token_count": r[13],
                "segment_index": r[14]
            })

    # 1 TXT chunk
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, cm.id, lg.id, l.id, a.id,
                   ts.chunk_type, ts.text, a.extracted_path, a.file_name,
                   ts.start_time_seconds, ts.end_time_seconds,
                   a.rag_enabled, ts.timestamp_confidence, ts.token_count,
                   ts.segment_index
            FROM transcript_segments ts
            JOIN transcripts t ON t.id = ts.transcript_id
            JOIN assets a ON a.id = t.id
            JOIN lessons l ON l.id = a.lesson_id
            JOIN lesson_groups lg ON lg.id = l.lesson_group_id
            JOIN course_modules cm ON cm.id = lg.module_id
            JOIN courses c ON c.id = cm.course_id
            WHERE ts.chunk_type = 'txt_window' AND ts.segment_index = 0
            ORDER BY a.asset_slug
            LIMIT 1
        """)
        for r in cur.fetchall():
            txt = r[6]
            records.append({
                "course_id": str(r[0]),
                "module_id": str(r[1]),
                "lesson_group_id": str(r[2]),
                "lesson_id": str(r[3]),
                "asset_id": str(r[4]),
                "modality": "transcript_txt",
                "chunk_type": r[5],
                "content": (txt[:400] + "...") if len(txt) > 400 else txt,
                "source_file": r[8],
                "source_path": r[7],
                "start_time_seconds": float(r[9]) if r[9] else None,
                "end_time_seconds": float(r[10]) if r[10] else None,
                "rag_enabled": bool(r[11]),
                "timestamp_confidence": r[12],
                "token_count": r[13],
                "segment_index": r[14]
            })

    # 2 HTML readings
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, cm.id, lg.id, l.id, a.id,
                   r.reading_subtype, r.extracted_text, a.extracted_path, a.file_name,
                   a.rag_enabled
            FROM readings r
            JOIN assets a ON a.id = r.id
            JOIN lessons l ON l.id = a.lesson_id
            JOIN lesson_groups lg ON lg.id = l.lesson_group_id
            JOIN course_modules cm ON cm.id = lg.module_id
            JOIN courses c ON c.id = cm.course_id
            WHERE a.rag_enabled = true
            ORDER BY a.asset_slug
            LIMIT 2
        """)
        for r in cur.fetchall():
            text = r[6] or ""
            records.append({
                "course_id": str(r[0]),
                "module_id": str(r[1]),
                "lesson_group_id": str(r[2]),
                "lesson_id": str(r[3]),
                "asset_id": str(r[4]),
                "modality": "reading",
                "chunk_type": "html_reading",
                "reading_subtype": r[5],
                "content": (text[:400] + "...") if len(text) > 400 else text,
                "source_file": r[8],
                "source_path": r[7],
                "start_time_seconds": None,
                "end_time_seconds": None,
                "rag_enabled": bool(r[9]),
                "timestamp_confidence": None,
                "token_count": None,
                "segment_index": None
            })

out = Path("docs/sample_rag_records.json")
out.write_text(json.dumps(records, indent=2, default=str), encoding="utf-8")
print(f"Written {len(records)} sample records to {out}")
