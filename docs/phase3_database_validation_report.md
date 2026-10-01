# Phase 3 Database Validation Report
## IBM Data Science Professional Certificate — Coursera Multimodal Intelligence Platform

**Generated:** 2026-09-19
**Pipeline Version:** 2.0
**Report Author:** Database & Preprocessing Team

---

## 1. Execution Summary

| Item | Result |
|------|--------|
| Pipeline runs executed | 3 (initial + 2 idempotency tests) |
| Pipeline failures | 0 |
| Total pipeline duration | ~3.8 seconds (final run) |
| Source ZIP modified | NO — untouched throughout |
| Automated tests | **93/93 passed** |
| Overall Phase 3 status | **COMPLETE** |

### Bugs Found and Fixed in Phase 3

| # | Bug | Root Cause | Fix |
|---|-----|-----------|-----|
| 1 | `preprocessing/html/` shadowed stdlib `html` module | Python package named `html` same as stdlib | Renamed to `preprocessing/html_proc/` |
| 2 | Rich console `UnicodeEncodeError` on Windows CP1252 | Unicode checkmark and box-drawing chars in log messages | Replaced with ASCII + forced UTF-8 console |
| 3 | `extract_text()` returned empty string for all 22 HTML files | `lxml` silently discards HTML fragment content (no html/body tags) | Switched to `html.parser` which handles fragments correctly |
| 4 | `data_quality_issues` duplicated on re-runs | `ON CONFLICT DO NOTHING` without a unique constraint key | Clear table before each DQ run (full re-evaluation semantics) |

---

## 2. PostgreSQL Connection

| Parameter | Value |
|-----------|-------|
| Host | localhost |
| Port | 5432 |
| Database | coursera_platform |
| User | coursera_user |
| PostgreSQL version | 18 |
| Connection status | CONNECTED |
| Credentials source | .env file only — never in source code |

---

## 3. Database Schema Validation

All 12 required tables created successfully:
assets, course_modules, courses, data_quality_issues, lesson_groups, lessons,
processing_jobs, readings, transcript_segments, transcripts, video_segments, videos

Schema integrity confirmed:
- Primary keys: all tables have UUID PKs with gen_random_uuid() default
- Foreign keys: all parent-child relationships enforced
- Unique constraints: asset_slug, course_slug, module_slug uniqueness enforced
- updated_at auto-update triggers applied to all mutable tables
- No VECTOR columns — embedding storage deferred to AI/RAG team
- rag_enabled field present on assets table

---

## 4. Actual Database Record Counts

| Table | Count |
|-------|------:|
| courses | 1 |
| course_modules | 4 |
| lesson_groups | 12 |
| lessons | 65 |
| assets | 157 |
| videos | 0 (skipped --skip-video) |
| video_segments | 0 (skipped) |
| transcripts | 90 (45 SRT + 45 TXT) |
| transcript_segments | 3,382 (3,280 SRT + 102 TXT) |
| readings | 22 |
| processing_jobs | 0 (not tracked in pipeline v2) |
| data_quality_issues | 0 (all resolved after HTML fix) |

### Assets by Category
| Category | Count |
|----------|------:|
| video | 45 |
| transcript_srt | 45 |
| transcript_txt | 45 |
| reading | 17 |
| infographic | 1 |
| assignment | 1 |
| administrative | 3 |
| TOTAL | 157 |

### RAG Enablement
| rag_enabled | Count |
|-------------|------:|
| true | 154 |
| false | 3 (administrative assets only) |

---

## 5. Course Hierarchy Validation

IBM Data Science Professional Certificate (1 course)
- Module 01: Defining Data Science and What Data Scientists Do [is_optional=false]
  - G01: Welcome To The Course (4 lessons)
  - G02: Defining Data Science (6 lessons)
  - G03: What Do Data Scientists Do (7 lessons)
- Module 02: Data Science Topics [is_optional=false]
  - G01: Big Data And Data Mining (9 lessons)
  - G02: Deep Learning And Machine Learning (7 lessons)
- Module 03: Applications and Careers in Data Science [is_optional=false]
  - G01: Data Science Application Domains (6 lessons)
  - G02: Careers And Recruiting In Data Science (7 lessons)
  - G03: Final Assignment (1 lesson)
  - G04: Course Wrap Up (3 lessons)
  - G05: Digital Badge (1 lesson)
- Module 04: Data Literacy for Data Science (Optional) [is_optional=TRUE]
  - G01: Understanding Data (5 lessons)
  - G02: Data Literacy (9 lessons)

Totals: 1 course -> 4 modules -> 12 lesson groups -> 65 lessons -> 157 assets
Module 04 is_optional = true -- CONFIRMED CORRECT

---

## 6. SRT Transcript Validation

| Metric | Value |
|--------|------:|
| Total SRT transcripts | 45 |
| Successfully parsed | 45 |
| Failed | 0 |
| Total SRT caption segments | 3,280 |
| Empty caption text | 0 |
| Bad timestamps (end < start) | 0 |
| Missing timestamps | 0 |
| timestamp_confidence = high | 3,280 (100%) |

SRT validation: PASS

---

## 7. TXT Transcript Validation

| Metric | Value |
|--------|------:|
| Total TXT transcripts | 45 |
| Successfully processed | 45 |
| Failed | 0 |
| Total chunks | 102 |
| Minimum chunk tokens | 77 |
| Maximum chunk tokens | 500 |
| Average chunk tokens | 387 |
| Timestamp-aligned chunks | 102 (100%) |
| Chunks without timestamp | 0 |

All 102 TXT chunks have SRT-aligned timestamps (timestamp_confidence = low).

---

## 8. HTML / Readings Validation

| Metric | Value |
|--------|------:|
| Total HTML files | 22 |
| Successfully processed | 22 |
| Failed | 0 |
| With embedded base64 image | 3 |

Reading subtypes: lesson_overview=8, lesson_summary=5, administrative=3,
tips=2, course_syllabus=1, assignment=1, infographic=1, other=1

Fix applied: Coursera HTML files are fragments (start with meta charset + co-content, no html/body tags).
lxml silently produced empty output. Switched to html.parser -- all 22 files now extract correctly.

---

## 9. RAG Metadata Validation

RAG-excluded assets (3 total):
- 04_02_congrats-next-steps_instructions.html (administrative)
- 04_03_course-team-and-acknowledgements_instructions.html (administrative)
- 05_01_ibm-digital-badge_instructions.html (administrative)

154 of 157 assets are rag_enabled=true.

---

## 10. Idempotency Test

Pipeline executed 3 times. After the DQ idempotency fix:
- All tables: 0 diff between runs (PASS)
- data_quality_issues: cleared and rebuilt on each run (0 accumulation)

IDEMPOTENCY RESULT: PASSED

---

## 11. Referential Integrity Test

All orphan checks: 0 (PASS)
- orphan assets, orphan lessons, orphan lesson_groups, orphan modules
- orphan videos, orphan transcripts, orphan readings, orphan transcript_segments

REFERENTIAL INTEGRITY: PASSED

---

## 12. Data Quality Results

Final state: 0 DQ issues.

Previous 20 issues (before fix): All "Very short/empty extracted text (0 words)" for 22 HTML files.
Root cause: lxml parser issue. Fixed by switching to html.parser.

---

## 13. Automated Test Results

93 passed in 0.69s

| Test Module | Tests | Passed |
|-------------|------:|-------:|
| test_html_extractor.py | 21 | 21 |
| test_srt_parser.py | 21 | 21 |
| test_txt_chunker.py | 21 | 21 |
| test_utils.py | 30 | 30 |
| TOTAL | 93 | 93 |

---

## 14. Remaining Items

| Issue | Status |
|-------|--------|
| videos/video_segments empty | EXPECTED (--skip-video flag; ffmpeg not configured) |
| processing_jobs empty | EXPECTED (not implemented in v2 pipeline) |
| 1 reading subtype=other | LOW (valid content, informational only) |
| Module 04 is_optional but rag_enabled | INTENTIONAL (per Phase 2 approved decision) |

---

## 15. Phase 3 Final Status: COMPLETE

All 20 validation steps PASSED.
Phase 4 (AI/RAG implementation) may begin after review.
