# AI/RAG Team — Data Contract
## IBM Data Science Professional Certificate

**Version:** 1.0.0
**Date:** 2026-09-19
**Prepared by:** Database & Preprocessing Team
**For:** AI/RAG Implementation Team

---

## 1. Contract Purpose

This document defines the stable interface between the **Database & Preprocessing** layer and the **AI/RAG** layer for the Coursera Multimodal Intelligence Platform.

The preprocessing pipeline has completed Phase 3. All structured course data is now available in PostgreSQL (`coursera_platform`). This document describes exactly what data is available, how to query it, what fields are guaranteed, and what constraints apply.

---

## 2. Database Connection

```python
# Read from .env — NEVER hardcode credentials
import psycopg
conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="coursera_platform",
    user="coursera_user",
    password="<from .env>"
)
```

Or using the shared settings:
```python
from preprocessing.common.config import settings
from preprocessing.common.db import get_db

with get_db() as conn:
    # your queries here
    pass
```

---

## 3. Available Data

### 3.1 Record Counts (Guaranteed Minimums)

| Table | Rows | Notes |
|-------|-----:|-------|
| courses | 1 | IBM Data Science Professional Certificate |
| course_modules | 4 | Modules 01-04 |
| lesson_groups | 12 | Groups within modules |
| lessons | 65 | Individual lesson items |
| assets | 157 | All course files |
| transcripts | 90 | 45 SRT + 45 TXT |
| transcript_segments | 3,382 | 3,280 SRT captions + 102 TXT chunks |
| readings | 22 | Processed HTML files |
| videos | 0 | Populated when ffmpeg is configured |

### 3.2 Modalities Available

| Modality | Table | Count |
|----------|-------|------:|
| SRT caption segments (timestamped) | `transcript_segments` WHERE `chunk_type='srt_caption'` | 3,280 |
| TXT semantic chunks (SRT-aligned) | `transcript_segments` WHERE `chunk_type='txt_window'` | 102 |
| HTML readings | `readings` | 22 |
| Videos (metadata) | `videos` | 0 (pending ffmpeg setup) |

### 3.3 RAG-Ready Records

Only query records where `assets.rag_enabled = true`.

```sql
-- All RAG-ready assets
SELECT * FROM assets WHERE rag_enabled = true;
-- Count: 154
```

RAG-excluded assets (3 total):
- Administrative pages: badge, congratulations, course team

---

## 4. Key Queries for AI/RAG Team

### 4.1 Get All RAG-Ready SRT Caption Segments with Full Lineage

```sql
SELECT
    ts.id              AS segment_id,
    ts.segment_index,
    ts.text            AS content,
    ts.token_count,
    ts.start_time_seconds,
    ts.end_time_seconds,
    ts.timestamp_confidence,  -- 'high' for SRT
    a.id               AS asset_id,
    a.asset_slug,
    a.file_name,
    a.checksum_sha256,
    l.lesson_title,
    lg.group_title,
    cm.module_number,
    cm.module_title,
    cm.is_optional,
    c.course_name
FROM transcript_segments ts
JOIN transcripts t ON t.id = ts.transcript_id
JOIN assets a ON a.id = t.id
JOIN lessons l ON l.id = a.lesson_id
JOIN lesson_groups lg ON lg.id = l.lesson_group_id
JOIN course_modules cm ON cm.id = lg.module_id
JOIN courses c ON c.id = cm.course_id
WHERE ts.chunk_type = 'srt_caption'
  AND a.rag_enabled = true
ORDER BY a.asset_slug, ts.segment_index;
```

**Expected rows:** 3,280

### 4.2 Get All RAG-Ready TXT Semantic Chunks with Full Lineage

```sql
SELECT
    ts.id              AS segment_id,
    ts.segment_index,
    ts.text            AS content,
    ts.token_count,
    ts.start_time_seconds,
    ts.end_time_seconds,
    ts.timestamp_confidence,  -- 'low' for TXT (SRT-aligned)
    a.id               AS asset_id,
    a.asset_slug,
    a.file_name,
    l.lesson_title,
    lg.group_title,
    cm.module_number,
    cm.module_title
FROM transcript_segments ts
JOIN transcripts t ON t.id = ts.transcript_id
JOIN assets a ON a.id = t.id
JOIN lessons l ON l.id = a.lesson_id
JOIN lesson_groups lg ON lg.id = l.lesson_group_id
JOIN course_modules cm ON cm.id = lg.module_id
WHERE ts.chunk_type = 'txt_window'
  AND a.rag_enabled = true
ORDER BY a.asset_slug, ts.segment_index;
```

**Expected rows:** 102

### 4.3 Get All RAG-Ready HTML Readings with Full Lineage

```sql
SELECT
    r.id               AS reading_id,
    r.extracted_text   AS content,
    r.reading_subtype,
    r.raw_html,
    r.has_embedded_image,
    r.embedded_image_path,
    a.id               AS asset_id,
    a.asset_slug,
    a.file_name,
    a.checksum_sha256,
    l.lesson_title,
    lg.group_title,
    cm.module_number,
    cm.module_title
FROM readings r
JOIN assets a ON a.id = r.id
JOIN lessons l ON l.id = a.lesson_id
JOIN lesson_groups lg ON lg.id = l.lesson_group_id
JOIN course_modules cm ON cm.id = lg.module_id
WHERE a.rag_enabled = true
ORDER BY a.asset_slug;
```

**Expected rows:** 19 (22 total - 3 administrative)

---

## 5. Field Contracts

### 5.1 `transcript_segments` (Primary RAG Source)

| Field | Type | Guaranteed | Notes |
|-------|------|-----------|-------|
| `id` | UUID | YES | Stable, permanent ID |
| `transcript_id` | UUID FK | YES | Links to `transcripts` (which shares ID with `assets`) |
| `segment_index` | INTEGER | YES | 1-based ordering within transcript; sequential |
| `text` | TEXT | YES | Non-empty, normalized whitespace |
| `chunk_type` | ENUM | YES | `'srt_caption'` or `'txt_window'` |
| `token_count` | INTEGER | YES | tiktoken cl100k_base token count |
| `start_time_seconds` | FLOAT | YES (SRT), YES (TXT-aligned) | Seconds from video start |
| `end_time_seconds` | FLOAT | YES (SRT), YES (TXT-aligned) | Seconds from video end |
| `timestamp_confidence` | ENUM | YES | `'high'` (SRT), `'low'` (TXT/aligned), `'none'` |
| `srt_sequence_number` | INTEGER | SRT only | Original SRT block number |
| `start_char` | INTEGER | TXT only | Character offset in source text |
| `end_char` | INTEGER | TXT only | Character offset in source text |
| `embedding` | VECTOR | NOT YET | Reserved for AI/RAG team to populate |
| `created_at` | TIMESTAMPTZ | YES | Immutable after insert |

### 5.2 `readings`

| Field | Type | Guaranteed | Notes |
|-------|------|-----------|-------|
| `id` | UUID | YES | Same UUID as `assets.id` (1:1 relationship) |
| `reading_subtype` | ENUM | YES | `lesson_overview`, `lesson_summary`, `course_syllabus`, `assignment`, `infographic`, `administrative`, `tips`, `other` |
| `extracted_text` | TEXT | YES | Clean prose text, lxml-parsed with whitespace normalized |
| `raw_html` | TEXT | YES | Full original HTML for re-parsing if needed |
| `has_embedded_image` | BOOLEAN | YES | True if base64 image was extracted |
| `embedded_image_path` | TEXT | CONDITIONAL | Filesystem path to extracted image (if has_embedded_image=true) |
| `embedding` | VECTOR | NOT YET | Reserved for AI/RAG team |
| `created_at` | TIMESTAMPTZ | YES | Immutable after insert |

### 5.3 `assets`

| Field | Type | Guaranteed | Notes |
|-------|------|-----------|-------|
| `id` | UUID | YES | Stable, permanent ID; used as FK in videos/transcripts/readings |
| `lesson_id` | UUID FK | YES | Never NULL |
| `asset_slug` | VARCHAR(600) | YES | Unique, lowercase, forward-slash separated relative path |
| `file_name` | VARCHAR(400) | YES | Just the filename (no path) |
| `asset_type` | VARCHAR(20) | YES | `'video'`, `'subtitle'`, `'reading'`, `'infographic'`, `'assignment'` |
| `asset_category` | ENUM | YES | `'video'`, `'transcript_srt'`, `'transcript_txt'`, `'reading'`, `'infographic'`, `'assignment'`, `'administrative'` |
| `rag_enabled` | BOOLEAN | YES | **Use this to filter RAG corpus** |
| `checksum_sha256` | VARCHAR(64) | YES | SHA-256 of original file content; use for deduplication |
| `processing_status` | ENUM | YES | `'extracted'` (video, awaiting ffprobe) or `'processed'` (all others) |
| `extracted_path` | TEXT | YES | Relative filesystem path to extracted file in `data/raw/` |
| `file_size_bytes` | BIGINT | YES | Original file size |
| `mime_type` | VARCHAR(100) | YES | MIME type of asset |

### 5.4 `courses`

| Field | Type | Guaranteed | Notes |
|-------|------|-----------|-------|
| `id` | UUID | YES | `67378fb7-49db-4a81-ac0f-b290c6cb0649` |
| `course_name` | TEXT | YES | "IBM Data Science Professional Certificate" |
| `course_slug` | VARCHAR(300) | YES | Unique identifier |
| `course_description` | TEXT | OPTIONAL | NULL if not in source data |

### 5.5 `course_modules`

| Field | Type | Guaranteed | Notes |
|-------|------|-----------|-------|
| `module_number` | INTEGER | YES | 1, 2, 3, 4 |
| `module_title` | TEXT | YES | Human-readable title |
| `is_optional` | BOOLEAN | YES | Module 04 is TRUE — include in corpus, flag appropriately |

---

## 6. Data Lineage Guarantees

Every `transcript_segment` can be traced to:

```
transcript_segments.id
  └── transcripts.id (= assets.id)
        └── assets.lesson_id
              └── lessons.lesson_group_id
                    └── lesson_groups.module_id
                          └── course_modules.course_id
                                └── courses.id
```

This means every text chunk carries:
- Full course hierarchy context
- Source filename + SHA-256 checksum
- Exact video timestamp range (for SRT)
- `rag_enabled` flag

---

## 7. What AI/RAG Team Must NOT Modify

| Object | Why |
|--------|-----|
| All existing tables and columns | Preprocessing team owns schema; coordinate changes |
| `rag_enabled` flag values | Set by category rules; do not override without coordination |
| `id` values in any table | Stable UUIDs used as cross-table references |
| `checksum_sha256` values | Integrity verification keys |
| Original source files in `data/raw/` | Do not modify extracted source files |

---

## 8. What AI/RAG Team MAY Add

| Action | Notes |
|--------|-------|
| Add `embedding VECTOR(1536)` column to `transcript_segments` | Use migration in `database/migrations/` |
| Add `embedding VECTOR(1536)` column to `readings` | Migration already partially defined in `001_add_rag_embedding_columns.sql` |
| Add `pgvector` extension | Run: `CREATE EXTENSION IF NOT EXISTS vector;` as superuser |
| Add new tables for vector indexes | Use separate migration files |
| Query any table via read-only queries | All tables are available |
| Store embeddings back to `transcript_segments.embedding` | After computing with OpenAI/Gemini |

---

## 9. Embedding Migration Template

The stub migration is at `database/migrations/001_add_rag_embedding_columns.sql`.

To activate:

```sql
-- Run as postgres superuser first:
CREATE EXTENSION IF NOT EXISTS vector;

-- Then run the migration:
ALTER TABLE transcript_segments ADD COLUMN IF NOT EXISTS embedding vector(1536);
ALTER TABLE readings ADD COLUMN IF NOT EXISTS embedding vector(1536);

-- Create HNSW index for similarity search:
CREATE INDEX CONCURRENTLY idx_ts_embedding
  ON transcript_segments USING hnsw (embedding vector_cosine_ops);

CREATE INDEX CONCURRENTLY idx_readings_embedding
  ON readings USING hnsw (embedding vector_cosine_ops);
```

---

## 10. Sample Queries for RAG Retrieval

### Similarity Search (after embeddings are populated)

```sql
-- Find top-5 most similar SRT segments to a query embedding
SELECT
    ts.text,
    ts.start_time_seconds,
    ts.end_time_seconds,
    a.file_name,
    l.lesson_title,
    cm.module_number,
    1 - (ts.embedding <=> '[0.01, 0.02, ...]'::vector) AS similarity
FROM transcript_segments ts
JOIN transcripts t ON t.id = ts.transcript_id
JOIN assets a ON a.id = t.id
JOIN lessons l ON l.id = a.lesson_id
JOIN lesson_groups lg ON lg.id = l.lesson_group_id
JOIN course_modules cm ON cm.id = lg.module_id
WHERE ts.chunk_type = 'srt_caption'
  AND a.rag_enabled = true
ORDER BY ts.embedding <=> '[0.01, 0.02, ...]'::vector
LIMIT 5;
```

### Filter by Module

```sql
WHERE cm.module_number = 1  -- Restrict to Module 01
```

### Filter by Timestamp Range

```sql
WHERE ts.start_time_seconds BETWEEN 0 AND 120  -- First 2 minutes only
```

### Exclude Optional Module

```sql
WHERE cm.is_optional = false  -- Exclude Module 04
```

---

## 11. Important Notes

1. **Module 04 is included in the RAG corpus** (`rag_enabled = true`) but `is_optional = true`. The AI/RAG team may choose to weight it differently or filter it with `WHERE cm.is_optional = false` if needed.

2. **TXT chunks have `timestamp_confidence = 'low'`** — they are aligned to SRT timestamps by word overlap, not exact timing. Use SRT segments when precise timestamp evidence is required.

3. **SRT segments have `timestamp_confidence = 'high'`** — exact timestamps from the subtitle files.

4. **3 HTML readings have embedded images extracted** — the `embedded_image_path` field points to `data/processed/images/` where the PNG/JPG was saved. The `raw_html` field still contains the full original HTML if needed.

5. **Videos table is empty** — `--skip-video` was used in this pipeline run. When ffmpeg/ffprobe is available, re-run the pipeline without `--skip-video` to populate video metadata and `video_segments`.

6. **Source ZIP is untouched** — `IBM Data Science Professional Certificate.zip` was never modified. All data was extracted to `data/raw/`.

---

## 12. Contract Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-09-19 | Initial Phase 3 release |
