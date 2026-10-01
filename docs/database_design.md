# Database Design — IBM Data Science Professional Certificate

**Designed:** 2026-09-19  
**Basis:** Actual dataset inspection only — no tables invented for hypothetical features  
**Target DBMS:** PostgreSQL 15+

---

## Entity-Relationship Overview

```
courses
  └──< course_modules
         └──< lesson_groups
                └──< lessons
                       └──< assets (polymorphic by asset_category)
                              ├── videos        (one per video lesson)
                              ├── transcripts   (two per video: SRT + TXT)
                              └── readings      (HTML instruction pages)

assets
  └──< processing_jobs      (track preprocessing state)
  └──< data_quality_issues  (DQ findings per asset)

videos
  └──< video_segments       (timestamp-based chunks for RAG)

transcripts
  └──< transcript_segments  (text chunks for RAG)
```

---

## Tables

---

### `courses`

**Purpose:** Top-level course record. One row per course.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | Stable unique identifier |
| `course_slug` | `VARCHAR(200)` | UNIQUE NOT NULL | e.g. `ibm-ds-prof-cert-v1` |
| `course_name` | `VARCHAR(500)` | NOT NULL | Full human-readable name |
| `source` | `VARCHAR(100)` | NOT NULL DEFAULT `'authorized_local_dataset'` | Data provenance |
| `zip_path` | `TEXT` | | Original ZIP archive absolute path |
| `root_folder` | `TEXT` | | Root folder name inside ZIP |
| `total_assets` | `INT` | | Denormalized count for quick stats |
| `is_optional` | `BOOLEAN` | NOT NULL DEFAULT `FALSE` | Whether entire course is optional |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |

**Indexes:** `course_slug` (UNIQUE)

---

### `course_modules`

**Purpose:** Top-level modules (the numbered folders inside the course root, e.g., `01_defining-data-science-...`).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | |
| `course_id` | `UUID` | FK → `courses(id)` ON DELETE CASCADE | |
| `module_slug` | `VARCHAR(300)` | NOT NULL | e.g. `01_defining-data-science-and-what-data-scientists-do` |
| `module_number` | `SMALLINT` | NOT NULL | Numeric prefix (1, 2, 3, 4) |
| `module_title` | `VARCHAR(500)` | NOT NULL | Human-readable title |
| `is_optional` | `BOOLEAN` | NOT NULL DEFAULT `FALSE` | `true` for module 04 |
| `sort_order` | `SMALLINT` | NOT NULL | Display ordering |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |

**Indexes:** `(course_id, module_number)` UNIQUE  
**FK:** `course_id` → `courses(id)`

---

### `lesson_groups`

**Purpose:** Sub-folders within a module (e.g., `01_welcome-to-the-course`, `02_defining-data-science`). Corresponds to what Coursera calls "weeks" or "lesson sections."

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | |
| `module_id` | `UUID` | FK → `course_modules(id)` ON DELETE CASCADE | |
| `group_slug` | `VARCHAR(300)` | NOT NULL | Folder name slug |
| `group_number` | `SMALLINT` | NOT NULL | Numeric prefix within module |
| `group_title` | `VARCHAR(500)` | NOT NULL | Human-readable title |
| `sort_order` | `SMALLINT` | NOT NULL | Display ordering |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |

**Indexes:** `(module_id, group_number)` UNIQUE  
**FK:** `module_id` → `course_modules(id)`

---

### `lessons`

**Purpose:** Individual lesson items — each lesson corresponds to one video (or one HTML reading) identified by its `NN_NN_` prefix. A lesson is the atomic unit of instructional content.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | |
| `lesson_group_id` | `UUID` | FK → `lesson_groups(id)` ON DELETE CASCADE | |
| `lesson_slug` | `VARCHAR(400)` | NOT NULL | Base filename stem, e.g. `02_02_what-is-data-science` |
| `lesson_prefix` | `VARCHAR(10)` | NOT NULL | e.g. `02_02` |
| `lesson_title` | `VARCHAR(500)` | NOT NULL | Human-readable from slug |
| `lesson_type` | `VARCHAR(50)` | NOT NULL CHECK IN (`'video_lesson'`, `'reading'`, `'assignment'`, `'administrative'`) | |
| `is_summary` | `BOOLEAN` | NOT NULL DEFAULT `FALSE` | `true` for lesson-summary items |
| `is_overview` | `BOOLEAN` | NOT NULL DEFAULT `FALSE` | `true` for lesson-overview items |
| `sort_order` | `SMALLINT` | NOT NULL | |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |

**Indexes:** `(lesson_group_id, lesson_prefix)` UNIQUE; `lesson_slug`  
**FK:** `lesson_group_id` → `lesson_groups(id)`

---

### `assets`

**Purpose:** Central asset registry — one row per physical file. Polymorphic table; specialized tables (`videos`, `transcripts`, `readings`) hold type-specific metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | |
| `lesson_id` | `UUID` | FK → `lessons(id)` ON DELETE CASCADE | |
| `asset_slug` | `VARCHAR(500)` | UNIQUE NOT NULL | Relative path within ZIP (stable) |
| `file_name` | `VARCHAR(400)` | NOT NULL | Basename of file |
| `file_type` | `VARCHAR(20)` | NOT NULL | `mp4`, `srt`, `txt`, `html` |
| `mime_type` | `VARCHAR(100)` | NOT NULL | MIME type string |
| `asset_category` | `VARCHAR(50)` | NOT NULL CHECK IN (`'video'`, `'transcript_srt'`, `'transcript_txt'`, `'reading'`, `'infographic'`, `'assignment'`, `'administrative'`) | |
| `size_bytes` | `BIGINT` | NOT NULL | Uncompressed size |
| `last_modified_zip` | `TIMESTAMPTZ` | | Modification timestamp from ZIP entry |
| `zip_compressed_bytes` | `BIGINT` | | Compressed size in ZIP |
| `processing_status` | `VARCHAR(30)` | NOT NULL DEFAULT `'pending'` CHECK IN (`'pending'`, `'extracted'`, `'processed'`, `'failed'`, `'skipped'`) | Pipeline state |
| `extracted_path` | `TEXT` | | Absolute path after extraction to `data/raw/` |
| `processed_path` | `TEXT` | | Absolute path in `data/processed/` |
| `checksum_sha256` | `CHAR(64)` | | SHA-256 of raw extracted file |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |

**Indexes:** `asset_slug` (UNIQUE); `(lesson_id, asset_category)`; `processing_status`; `file_type`  
**FK:** `lesson_id` → `lessons(id)`

---

### `videos`

**Purpose:** Video-specific metadata extracted during preprocessing (requires `ffprobe`/extraction).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK = FK → `assets(id)` | 1:1 with the asset row |
| `duration_seconds` | `NUMERIC(10,3)` | | Total video duration |
| `width_px` | `INT` | | Frame width |
| `height_px` | `INT` | | Frame height |
| `frame_rate` | `NUMERIC(8,3)` | | Frames per second |
| `video_codec` | `VARCHAR(50)` | | e.g. `h264` |
| `audio_codec` | `VARCHAR(50)` | | e.g. `aac` |
| `audio_channels` | `SMALLINT` | | |
| `audio_sample_rate_hz` | `INT` | | |
| `has_audio` | `BOOLEAN` | NOT NULL DEFAULT `TRUE` | |
| `container_format` | `VARCHAR(50)` | | e.g. `mp4` |
| `bit_rate_kbps` | `INT` | | |
| `metadata_raw` | `JSONB` | | Full ffprobe JSON output |
| `extracted_at` | `TIMESTAMPTZ` | | When ffprobe was run |

**FK:** `id` → `assets(id)` ON DELETE CASCADE  
**Indexes:** `duration_seconds`, `(width_px, height_px)`

---

### `video_segments`

**Purpose:** Time-based chunks of a video for RAG retrieval. Each segment links to its corresponding transcript segment.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | |
| `video_id` | `UUID` | FK → `videos(id)` ON DELETE CASCADE | |
| `segment_index` | `INT` | NOT NULL | 0-based chunk number |
| `start_seconds` | `NUMERIC(10,3)` | NOT NULL | |
| `end_seconds` | `NUMERIC(10,3)` | NOT NULL | |
| `transcript_text` | `TEXT` | | Corresponding transcript text for this time range |
| `token_count` | `INT` | | Approx. LLM token count |
| `embedding_model` | `VARCHAR(100)` | | Model used to generate embedding |
| `embedding` | `VECTOR(1536)` | | pgvector embedding (populated by AI/RAG team) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |

**Indexes:** `(video_id, segment_index)` UNIQUE; `video_id`  
**FK:** `video_id` → `videos(id)`  
**Note:** Requires `pgvector` extension for `embedding` column.

---

### `transcripts`

**Purpose:** Transcript-specific metadata. Two rows per video lesson (one for SRT, one for TXT).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK = FK → `assets(id)` | 1:1 with asset row |
| `video_asset_id` | `UUID` | FK → `assets(id)` | Corresponding video asset |
| `transcript_format` | `VARCHAR(10)` | NOT NULL CHECK IN (`'srt'`, `'txt'`) | |
| `language_code` | `VARCHAR(10)` | NOT NULL DEFAULT `'en'` | |
| `char_count` | `INT` | | |
| `word_count` | `INT` | | |
| `line_count` | `INT` | | |
| `has_timestamps` | `BOOLEAN` | NOT NULL | `true` for SRT, `false` for TXT |
| `encoding` | `VARCHAR(20)` | DEFAULT `'utf-8'` | |
| `cleaned_text` | `TEXT` | | Cleaned version stored here after preprocessing |
| `extracted_at` | `TIMESTAMPTZ` | | |

**FK:** `id` → `assets(id)` ON DELETE CASCADE; `video_asset_id` → `assets(id)`  
**Indexes:** `video_asset_id`; `transcript_format`

---

### `transcript_segments`

**Purpose:** Text chunks (for TXT transcripts) for RAG. Each segment is a contiguous passage suitable for embedding.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | |
| `transcript_id` | `UUID` | FK → `transcripts(id)` ON DELETE CASCADE | |
| `segment_index` | `INT` | NOT NULL | 0-based |
| `start_char` | `INT` | | Character offset in cleaned_text |
| `end_char` | `INT` | | |
| `start_time_seconds` | `NUMERIC(10,3)` | | From SRT alignment (nullable) |
| `end_time_seconds` | `NUMERIC(10,3)` | | From SRT alignment (nullable) |
| `text` | `TEXT` | NOT NULL | Chunk text |
| `token_count` | `INT` | | |
| `embedding_model` | `VARCHAR(100)` | | |
| `embedding` | `VECTOR(1536)` | | pgvector (AI/RAG team populates) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |

**Indexes:** `(transcript_id, segment_index)` UNIQUE; `transcript_id`  
**FK:** `transcript_id` → `transcripts(id)`

---

### `readings`

**Purpose:** HTML reading/instruction-page specific metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK = FK → `assets(id)` | |
| `reading_subtype` | `VARCHAR(50)` | NOT NULL CHECK IN (`'lesson_overview'`, `'lesson_summary'`, `'course_syllabus'`, `'assignment'`, `'infographic'`, `'administrative'`, `'tips'`) | |
| `raw_html` | `TEXT` | | Extracted HTML content |
| `extracted_text` | `TEXT` | | Stripped plain text (base64 blobs removed) |
| `has_embedded_image` | `BOOLEAN` | NOT NULL DEFAULT `FALSE` | `true` for large HTML with base64 PNG |
| `embedded_image_path` | `TEXT` | | Path to extracted PNG if applicable |
| `char_count` | `INT` | | |
| `word_count` | `INT` | | |
| `extracted_at` | `TIMESTAMPTZ` | | |

**FK:** `id` → `assets(id)` ON DELETE CASCADE

---

### `processing_jobs`

**Purpose:** Track the state and logs of each pipeline run per asset.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | |
| `asset_id` | `UUID` | FK → `assets(id)` | |
| `job_type` | `VARCHAR(50)` | NOT NULL | `'extraction'`, `'metadata_extraction'`, `'text_cleaning'`, `'segmentation'`, `'checksum'` |
| `status` | `VARCHAR(20)` | NOT NULL DEFAULT `'pending'` CHECK IN (`'pending'`, `'running'`, `'success'`, `'failed'`) | |
| `started_at` | `TIMESTAMPTZ` | | |
| `completed_at` | `TIMESTAMPTZ` | | |
| `duration_ms` | `INT` | | |
| `error_message` | `TEXT` | | |
| `log_output` | `TEXT` | | |
| `pipeline_version` | `VARCHAR(50)` | | Version tag of the pipeline run |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |

**Indexes:** `(asset_id, job_type)`; `status`  
**FK:** `asset_id` → `assets(id)`

---

### `data_quality_issues`

**Purpose:** Persistent record of all DQ problems found during audit and pipeline runs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, DEFAULT `gen_random_uuid()` | |
| `issue_code` | `VARCHAR(20)` | NOT NULL | e.g. `DQ-001` |
| `asset_id` | `UUID` | FK → `assets(id)` | Nullable if course-level |
| `severity` | `VARCHAR(20)` | NOT NULL CHECK IN (`'low'`, `'medium'`, `'high'`, `'info'`) | |
| `category` | `VARCHAR(50)` | NOT NULL | `'filename'`, `'encoding'`, `'content'`, `'relationship'`, `'metadata'`, `'validation'` |
| `description` | `TEXT` | NOT NULL | Human-readable description |
| `recommendation` | `TEXT` | | Remediation action |
| `resolved` | `BOOLEAN` | NOT NULL DEFAULT `FALSE` | |
| `resolved_at` | `TIMESTAMPTZ` | | |
| `detected_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT `NOW()` | |

**Indexes:** `(asset_id, issue_code)`; `severity`; `resolved`  
**FK:** `asset_id` → `assets(id)`

---

## Tables Explicitly NOT Created (and Why)

| Table | Reason Not Created |
|-------|-------------------|
| `quiz_questions` | No quiz data exists in dataset |
| `quiz_responses` | No quiz data exists in dataset |
| `assignments` | Only 1 assignment (HTML-based) — covered by `readings` + `data_quality_issues` |
| `discussions` | No discussion data in dataset |
| `slides` | No slide files in dataset |
| `images` | No standalone image files (only one embedded PNG) |
| `topics` / `asset_topics` | Could be useful for AI/RAG team but no source data; deferred to AI team |

---

## Extension Points (for AI/RAG Team)

The following can be added when the AI team begins work:

```sql
-- Add pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- The embedding columns in video_segments and transcript_segments
-- are already designed for pgvector (VECTOR(1536))
-- Change dimension to match your chosen embedding model
```

---

## Relationships Diagram

```
courses ──< course_modules ──< lesson_groups ──< lessons ──< assets
                                                               │
                              ┌────────────────────────────────┤
                              │                                │
                           videos                        transcripts
                              │                                │
                         video_segments              transcript_segments
                              │
                          readings
                              │
                      processing_jobs (per asset)
                      data_quality_issues (per asset)
```
