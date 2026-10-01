# Phase 2 Validation Report
## IBM Data Science Professional Certificate — Preprocessing Pipeline

**Generated:** 2026-09-30 18:59:02 UTC  
**Total pipeline time:** 28.7s

---

## Pipeline Step Summary

| Step | Duration | Succeeded | Failed | Status |
|------|----------|-----------|--------|--------|
| Extract ZIP | 1806ms | — | — | ✅ OK |
| Load to Database | 737ms | — | — | ✅ OK |
| Process SRT Transcripts | 10480ms | 45 | 0 | ✅ OK |
| Process TXT Transcripts | 223ms | 4 | 0 | ✅ OK |
| Process HTML Readings | 10293ms | 186 | 0 | ⏭ Skipped |
| Process Videos | 4787ms | 45 | 0 | ✅ OK |
| Data Quality Checks | 87ms | — | — | ✅ OK |

---

## Database Record Counts

| Table | Records |
|-------|--------:|
| courses | 1 |
| course_modules | 2 |
| lesson_groups | 2 |
| lessons | 1 |
| assets | 296 |
| videos | 45 |
| video_segments | 183 |
| transcripts | 49 |
| transcript_segments | 9479 |
| readings | 186 |
| data_quality_issues | 1 |

---

## Asset Processing Status

| Status | Count |
|--------|------:|
| processed | 280 |
| extracted | 16 |

---

## Asset Category Breakdown

| Category | Count |
|----------|------:|
| reading | 202 |
| transcript_srt | 45 |
| transcript_txt | 4 |
| video | 45 |

---

## Data Quality Issues

| Severity | Count |
|----------|------:|
| medium | 1 |

---

## Data Lineage Verification

- ✅ Every asset record contains: course → module → lesson → asset → source_file → checksum
- ✅ Every transcript links to its parent video via `video_asset_id`
- ✅ Every video_segment preserves `start_seconds` / `end_seconds` for time-anchored retrieval
- ✅ Every transcript_segment preserves `start_time_seconds` / `end_time_seconds` and `timestamp_confidence`
- ✅ Administrative assets are marked `rag_enabled = false`
- ✅ Optional module marked `is_optional = true`

---

## Source File Integrity

- ✅ Original ZIP not modified: `data\raw\dataset.zip`
- ✅ All files extracted to: `data\raw`
- ✅ Processed outputs in: `data\processed`
- ✅ No credentials in source code (read from .env)
- ✅ DB loaded idempotently — re-runs do not create duplicates

---

## Notes

- Embedding columns (VECTOR) deliberately omitted — AI/RAG team adds via `migrations/001_add_rag_embedding_columns.sql`
- `ffprobe` metadata extraction depends on `ffmpeg` being installed on the system
- If `SKIP_VIDEO_METADATA=true` in .env, video metadata columns remain NULL until ffprobe is available
