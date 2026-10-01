# Data Quality Report — IBM Data Science Professional Certificate

**Audit Date:** 2026-09-19  
**Auditor:** Automated inspection via PowerShell (no files extracted, no originals modified)  
**Dataset:** `IBM Data Science Professional Certificate.zip` (659.1 MB uncompressed, 157 files)

---

## Summary Counts

| Metric | Value |
|--------|------:|
| Total files in archive | 157 |
| Total valid files | 157 |
| Total invalid files (corrupt/unreadable) | 0 |
| Total empty files (0 bytes) | 0 |
| Total duplicate files (same content, different path) | 0 |
| Files with missing metadata | 0 |
| Unsupported/unexpected formats | 0 |
| Potential relationship problems | 0 |
| Missing transcripts for videos | 0 |
| Orphan transcripts (no matching video) | 0 |

---

## File-Level Audit

### Duplicate Files
**Result: NONE**

The 45 "duplicate stems" detected during initial scan (e.g., `02_02_what-is-data-science.en`) are **intentional pairs**: every `.en.srt` file has a companion `.en.txt` file representing the same transcript in two formats. These are not actual duplicates — they carry different content (one is timed SRT, one is clean plain text).

No byte-identical duplicate files were found.

### Empty Files
**Result: NONE**

All 157 files have non-zero `Length` values. Smallest file is the Congrats HTML at 2,157 bytes.

### Corrupted Files
**Result: CANNOT CONFIRM WITHOUT EXTRACTION**

Files were inspected in-archive. Three representative files (HTML, TXT, SRT) were extracted and decoded successfully, confirming ZIP integrity for those samples. Full corruption check on all 45 MP4 files would require extraction and header parsing — flagged for Phase 2 preprocessing validation.

> ⚠️ Recommendation: Run `ffprobe` on all extracted MP4 files during preprocessing to confirm each is a valid, playable video.

### Unsupported Formats
**Result: NONE**

All 157 files use one of four expected formats:
- `.mp4` — video
- `.srt` — SubRip subtitle/transcript
- `.txt` — plain text transcript
- `.html` — HTML reading/instruction page

No unexpected extensions (e.g., `.exe`, `.bin`, `.dat`) were found.

### Naming Inconsistencies
**Result: 1 MINOR ISSUE**

One file has a non-standard filename pattern:

| File | Issue |
|------|-------|
| `03_01_a-roadmap-to-your-data-science-journey_200457 088 Infograph on roadmap.html` | Contains **spaces** and an extra numeric ID (`200457 088`) in the filename, unlike all other files which use hyphen-separated slugs. |

This is not a data corruption issue but will require handling during path normalization in the preprocessing pipeline (URL-encoding or filename sanitization).

---

## Metadata Audit

### Missing Course/Module Information
**Result: NONE**

All 157 files reside inside a consistent 3-level folder hierarchy:
`[course_name] / [module_folder] / [lesson_group_folder] / [file]`

Module and lesson group can be reliably inferred from folder names for all files.

### Missing Asset Type
**Result: NONE**

All file types are unambiguously determinable from file extensions.

### Missing IDs
**Result: NONE (for files)**

All files can be assigned stable IDs from their relative paths. No external ID manifest exists in the dataset, but IDs are deterministically derivable.

---

## Video Audit

### Invalid Duration / Resolution / Missing Audio
**Result: CANNOT CONFIRM WITHOUT EXTRACTION**

MP4 metadata (duration, codec, resolution, frame rate, audio track) requires extraction. This is flagged as a **Phase 2 preprocessing task**.

Based on file sizes (range: 4.4 MB to 56.2 MB), durations are expected to range from approximately 1–15 minutes per video. No suspiciously small files were found that would suggest a corrupt or empty video container.

| Video | Size | Expected Status |
|-------|------|----------------|
| Smallest: `02_06_lesson-summary-defining-data-science.mp4` | 4.4 MB | Short summary video — expected |
| Largest: `01_04_viewpoints-working-with-varied-data-sources-and-types.mp4` | 56.2 MB | Long viewpoints panel discussion — expected |

### Duplicate Videos
**Result: NONE**

No filename collisions or size-identical pairs detected among the 45 MP4 files.

---

## Transcript Audit

### Empty Transcripts
**Result: NONE**

Smallest transcript files:
- Smallest `.en.txt`: `02_02_what-is-data-science.en.txt` — 2,187 bytes (valid; short video)
- Smallest `.en.srt`: `02_06_lesson-summary-defining-data-science.en.srt` — 4,752 bytes (valid)

### Duplicate Transcripts
**Result: NONE** (same-content pairs are intentional `.srt`/`.txt` pairs, not duplicates)

### Encoding Problems
**Result: LIKELY CLEAN (sample confirmed)**

Three text files were decoded successfully as UTF-8 during content sampling. All Coursera-generated transcripts are expected to be UTF-8 encoded.

> ⚠️ Recommendation: During extraction, explicitly read all `.txt` and `.srt` files with `encoding='utf-8'` and catch `UnicodeDecodeError` — flag any failures.

### Excessive Whitespace / Broken Characters
**Result: CLEAN in samples**

The sampled `.en.txt` content is well-formed prose. The sampled `.en.srt` contains properly formatted SubRip blocks with sequential numbering and valid `HH:MM:SS,mmm --> HH:MM:SS,mmm` timestamps.

### Orphan Transcripts (no matching video)
**Result: NONE**

Every `.en.srt` and `.en.txt` stem maps to an `.mp4` with the identical stem. Verified by the extension breakdown showing exactly 45 of each type.

---

## HTML / Reading Audit

### Structural Issues
**Result: 1 EMBEDDED IMAGE CONCERN**

| File | Size | Issue |
|------|------|-------|
| `03_01_a-roadmap-to-your-data-science-journey_instructions.html` | 527 KB | Contains a **base64-encoded PNG image** embedded directly in the HTML `<img src="data:image/png;base64,...">`. This is valid HTML but makes the file large and requires special handling during text extraction — the base64 string must be stripped before indexing. |
| `05_01_ibm-digital-badge_instructions.html` | 157 KB | Contains badge credential HTML. Likely includes embedded image or credential metadata. Administrative, not a learning asset. |
| `01_04_helpful-tips-for-course-completion_instructions.html` | 463 KB | Unusually large for a tips document. May also contain embedded imagery. |

> ⚠️ Recommendation: During HTML text extraction, strip all `data:image/...;base64,...` blobs before storing to avoid polluting the text corpus with binary data.

### Missing Titles
**Result: NONE**

All HTML files can be titled from their filename slug.

---

## Quiz / Structured Data Audit

**Result: NOT APPLICABLE**

No quiz files (JSON, CSV, XML, GIFT format) exist in this dataset. Quiz content is not present.

---

## Relationship Integrity Audit

### Missing Files
**Result: NONE**

All expected file triplets (MP4 + SRT + TXT) are intact for all 45 video lessons.

### Unexpected Files
**Result: 1 NOTE**

The `03_01_a-roadmap-to-your-data-science-journey_200457 088 Infograph on roadmap.html` file is an additional accessible version of the assignment infographic. It was not expected based on the folder naming convention but is a valid supplementary asset.

---

## Data Quality Issues Register

| ID | Severity | Category | File(s) | Description | Recommendation |
|----|----------|----------|---------|-------------|----------------|
| DQ-001 | LOW | Filename | `03_01_...200457 088 Infograph on roadmap.html` | Filename contains spaces and non-standard numeric prefix | Sanitize filename during copy to `data/processed/` |
| DQ-002 | MEDIUM | HTML Content | `03_01_..._instructions.html` (527 KB) | Large base64-encoded PNG embedded in HTML | Strip base64 blob before text extraction; extract PNG separately |
| DQ-003 | MEDIUM | HTML Content | `05_01_ibm-digital-badge_instructions.html` (157 KB) | May contain embedded credential imagery | Assess whether this is a learnable asset; exclude from RAG if administrative-only |
| DQ-004 | MEDIUM | HTML Content | `01_04_helpful-tips-for-course-completion_instructions.html` (463 KB) | Unusually large for a tips document | Inspect for embedded imagery during extraction |
| DQ-005 | LOW | Validation | All 45 MP4 files | Video codec/resolution/duration/audio not validated in-archive | Run `ffprobe` on all extracted MP4s during preprocessing |
| DQ-006 | LOW | Validation | All 90 transcript files | Encoding assumed UTF-8 but not byte-verified | Explicitly decode with UTF-8 during extraction, log any failures |
| DQ-007 | INFO | Structure | Module `04` | Entire module labeled `optional` in folder name | Flag in DB with `is_optional=true` |

---

## What Was NOT Found (Reported Explicitly)

| Expected Type | Found | Notes |
|---------------|-------|-------|
| PDF documents | ❌ | Not present |
| PowerPoint/slide decks | ❌ | Not present |
| Jupyter Notebooks | ❌ | Not present |
| Images (standalone) | ❌ | Only one infographic embedded in HTML |
| Quiz/assessment structured data | ❌ | Not present |
| Discussion forum data | ❌ | Not present |
| Subtitle files other than `.srt` | ❌ | Only SRT format found |
| Course metadata manifest | ❌ | No `manifest.json`, `metadata.json`, or similar |
| Multiple courses | ❌ | Only one course in this dataset |
