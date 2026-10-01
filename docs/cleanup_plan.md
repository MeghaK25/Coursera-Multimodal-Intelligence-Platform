# Cleanup Plan — Coursera Multimodal Intelligence Platform
## Generated: 2026-09-19

---

## Executive Summary

| Category | Count | Disk Impact |
|----------|------:|------------|
| NEVER DELETE | 3 files | 659 MB (ZIP alone) |
| KEEP — Required Code | 32 files | ~420 KB |
| KEEP — Documentation | 9 files | ~80 KB |
| KEEP — Configuration | 6 files | ~3 KB |
| KEEP — Source Data | data/raw/ (157 files) | 659 MB — REGENERABLE |
| KEEP — Processed Output | 3 images | ~840 KB — REGENERABLE |
| KEEP — Generated Report | 2 JSON files | ~12 KB — REGENERABLE |
| SAFE TO DELETE | __pycache__ dirs + .pyc | ~206 KB |
| SAFE TO DELETE | .pytest_cache/ | ~8 KB |
| SAFE TO DELETE | phase2_validation_report.md | ~3 KB |
| SAFE TO DELETE | logs/pipeline.log | ~50 KB |
| REVIEW | database/generate_sample_rag.py | ~5 KB |
| REVIEW | database/validate_phase3.py | ~16 KB |
| REVIEW | docs/phase3_raw_validation.json | ~6 KB |

**Total safe-to-delete: ~267 KB**
**Note: data/raw (659 MB) is 100% regenerable but proposed as KEEP — NOT safe to delete without explicit decision.**

---

## NEVER DELETE

These files are the source of truth for the entire project.

| Path | Reason | Risk if deleted |
|------|--------|----------------|
| `IBM Data Science Professional Certificate.zip` | Original authorized course dataset — SOLE source of truth. All of data/raw was extracted from this. | **CATASTROPHIC** — data/raw would become unrecoverable unless re-authorized |
| `database/schema.sql` | PostgreSQL schema — the blueprint for the entire 12-table database structure | **CRITICAL** — cannot reinitialize DB without this |
| `.env` | Live credentials connecting to coursera_platform database | **CRITICAL** — pipeline cannot connect to DB without this |

---

## KEEP — REQUIRED CODE

All production source code. None of this should be deleted.

| Path | Purpose |
|------|---------|
| `preprocessing/__init__.py` | Package marker |
| `preprocessing/extract_course.py` | Step 1: ZIP extraction, idempotent, checksum verification |
| `preprocessing/load_to_db.py` | Step 2: Full hierarchy upsert into PostgreSQL |
| `preprocessing/run_pipeline.py` | Master orchestrator — runs all 7 pipeline steps |
| `preprocessing/common/__init__.py` | Package marker |
| `preprocessing/common/config.py` | Pydantic settings, reads .env |
| `preprocessing/common/db.py` | psycopg3 helpers — get_db(), upsert_returning_id() |
| `preprocessing/common/logging_utils.py` | Centralized Rich logging with UTF-8 Windows fix |
| `preprocessing/common/models.py` | All Pydantic models + enums matching DB schema |
| `preprocessing/common/utils.py` | sha256_file, slug_from_path, asset_category_from_file, count_tokens |
| `preprocessing/transcript/__init__.py` | Package marker |
| `preprocessing/transcript/process_srt.py` | SRT parser → transcript_segments (confidence=high) |
| `preprocessing/transcript/process_txt.py` | 500-token chunker + SRT alignment (confidence=low) |
| `preprocessing/html_proc/__init__.py` | Package marker |
| `preprocessing/html_proc/process_html.py` | HTML extraction, base64 images, 8-way classification |
| `preprocessing/video/__init__.py` | Package marker |
| `preprocessing/video/process_videos.py` | ffprobe metadata + 300s segmentation |
| `preprocessing/assignment/__init__.py` | Package marker |
| `preprocessing/assignment/process_assignment.py` | Delegates HTML processing for assignment files |
| `preprocessing/quality/__init__.py` | Package marker |
| `preprocessing/quality/run_quality_checks.py` | 9 DQ check categories → data_quality_issues table |
| `database/init_db.py` | Schema initializer, supports --drop-existing |
| `database/setup_db.sql` | Manual SQL for DB + user creation (onboarding tool) |
| `database/migrations/001_add_rag_embedding_columns.sql` | AI/RAG team migration stub (VECTOR columns) |
| `tests/__init__.py` | Package marker |
| `tests/conftest.py` | Shared pytest fixtures |
| `tests/test_srt_parser.py` | 21 SRT tests |
| `tests/test_txt_chunker.py` | 21 TXT chunker tests |
| `tests/test_html_extractor.py` | 21 HTML extractor tests |
| `tests/test_utils.py` | 30 utility tests |

---

## KEEP — DOCUMENTATION

| Path | Purpose | Notes |
|------|---------|-------|
| `docs/course_structure.md` | Phase 1: Full course hierarchy map | Reference throughout project |
| `docs/asset_relationships.md` | Phase 1: How file types relate to each other | Architectural reference |
| `docs/data_quality_report.md` | Phase 1: 7 DQ issues found in raw data | Historical record |
| `docs/database_design.md` | Phase 1: Full schema design with rationale | Required for future schema changes |
| `docs/phase3_database_validation_report.md` | Phase 3: Complete validation results | Official phase sign-off document |
| `docs/ai_rag_data_contract.md` | Phase 3: Handoff contract for AI/RAG team | **Critical for next phase** |
| `docs/sample_rag_records.json` | Phase 3: 5 real DB records for AI/RAG team | **Critical for next phase** |

---

## KEEP — CONFIGURATION

| Path | Purpose | Notes |
|------|---------|-------|
| `.env.example` | Template for setting up credentials | Required for team onboarding |
| `.gitignore` | Prevents committing credentials, caches, raw data | Required when Git is initialized |
| `requirements.txt` | Python package dependencies for pip install | Required to reproduce the environment |
| `pytest.ini` | pytest configuration | Required to run tests |
| `README.md` | Project overview | Should be kept and potentially updated |

---

## KEEP — SOURCE DATA (REGENERABLE but KEEP)

| Path | Size | Regenerable? | Decision |
|------|------|-------------|---------|
| `data/raw/` (157 files, 4 module folders) | 659 MB | **YES** — via `python preprocessing/run_pipeline.py` or `python preprocessing/extract_course.py` from the ZIP | **KEEP** — regeneration takes ~1 second but the files serve as the working dataset for the pipeline |
| `data/inventory/course_inventory.json` | 155 KB | **YES** — regenerated every time extract_course.py runs | **KEEP** — used as input by load_to_db.py |
| `data/processed/images/` (3 PNG files) | 840 KB | **YES** — re-extracted by process_html.py on next run | **KEEP** — currently referenced by readings table (embedded_image_path). Deleting would leave dangling paths in DB. |

---

## SAFE TO DELETE

These files are automatically generated by Python/pytest and will be recreated on next run.
**Zero information loss. Zero risk.**

| Path | Type | Reason | Regenerable? | Size |
|------|------|--------|-------------|------|
| `preprocessing/__pycache__/` (3 .pyc files) | Python bytecode cache | Auto-generated by Python on import. Not source code. | YES — instantly on next `python` invocation | 23 KB |
| `preprocessing/common/__pycache__/` (6 .pyc files) | Python bytecode cache | Auto-generated | YES | 24 KB |
| `preprocessing/html_proc/__pycache__/` (2 .pyc files) | Python bytecode cache | Auto-generated | YES | 12 KB |
| `preprocessing/quality/__pycache__/` (2 .pyc files) | Python bytecode cache | Auto-generated | YES | 18 KB |
| `preprocessing/transcript/__pycache__/` (3 .pyc files) | Python bytecode cache | Auto-generated | YES | 29 KB |
| `tests/__pycache__/` (6 .pyc files) | Python bytecode cache | Auto-generated by pytest | YES | 99 KB |
| `.pytest_cache/` | pytest cache | Contains lastfailed, nodeids — recreated on next pytest run | YES | 8 KB |
| `docs/phase2_validation_report.md` | Auto-generated report | **Written by run_pipeline.py on every run** (line 248 of run_pipeline.py). Contains garbled encoding (mojibake Unicode chars). Superseded by the much more complete phase3_database_validation_report.md. | YES — regenerated every pipeline run | 3 KB |

**Total safe-to-delete: ~267 KB**

---

## REVIEW — Uncertain items requiring your decision

These files have value but their classification needs your explicit decision:

### 1. `database/generate_sample_rag.py` (5 KB)
- **What it is:** Script that queries the DB and writes docs/sample_rag_records.json
- **Is it imported?** No — standalone script only
- **Referenced by docs?** docs/sample_rag_records.json is a deliverable; this script generated it
- **Can sample_rag_records.json be regenerated?** YES — by running this script again
- **Risk if deleted:** Low — sample_rag_records.json already exists. Would need to rewrite script to regenerate.
- **Recommendation:** KEEP — useful maintenance tool for AI/RAG team to regenerate samples

### 2. `database/validate_phase3.py` (16 KB)
- **What it is:** Comprehensive DB validation query suite (16 validation checks, writes phase3_raw_validation.json)
- **Is it imported?** No — standalone script only
- **Is it part of the documented architecture?** YES — runs all Phase 3 validation queries
- **Risk if deleted:** Medium — would need to be rewritten to re-validate DB state in future
- **Recommendation:** KEEP — valuable maintenance and regression tool

### 3. `docs/phase3_raw_validation.json` (6 KB)
- **What it is:** Raw JSON output from validate_phase3.py — machine-readable validation snapshot
- **Is it referenced by other docs?** No
- **Can it be regenerated?** YES — by running validate_phase3.py
- **Risk if deleted:** Low — pure generated output from DB queries
- **Recommendation:** SAFE TO DELETE or KEEP — lightweight file, harmless to keep

### 4. `logs/pipeline.log` (50 KB)
- **What it is:** Log output from the last pipeline run (Unicode garbled on some entries due to CP1252 issue)
- **Is it required?** No — logs are regenerated on every run
- **Risk if deleted:** Low — it is a log file
- **Recommendation:** SAFE TO DELETE — logs/ directory should remain (pipeline writes here). Only the log file itself can go.
- **Note:** .gitignore already excludes logs/

---

## NOT PRESENT — Items that were confirmed cleaned up already

| Item | Status |
|------|--------|
| `database/read_pgadmin.py` | ALREADY DELETED in Phase 3 cleanup |
| `database/fetch_uuids.py` | ALREADY DELETED in Phase 3 cleanup |
| `preprocessing/html/` (original bad package name) | ALREADY RENAMED to `preprocessing/html_proc/` |
| `__zip_entries.json` | NOT PRESENT — not generated |
| `*.tmp`, `*.bak`, `*.swp` | NOT PRESENT — none found |
| `Thumbs.db`, `.DS_Store` | NOT PRESENT — none found |
| `venv/`, `.venv/` | NOT PRESENT — no virtual env in project dir |

---

## DATA/RAW Analysis

`data/raw/` contains exactly 157 files extracted from the ZIP:
- 45 MP4 video files
- 45 SRT subtitle files
- 45 TXT transcript files
- 22 HTML reading files

**Is it REGENERABLE?** YES — 100%. Running:
```
python preprocessing/extract_course.py
```
or
```
python preprocessing/run_pipeline.py --force-extract
```
will re-extract all 157 files from the ZIP in ~1 second.

**Should it be deleted?** NO — recommended to keep:
- It is the active working dataset
- Pipeline steps (SRT, TXT, HTML processors) read from data/raw/
- Without it, the pipeline cannot run without first re-extracting
- 659 MB is the uncompressed size of the ZIP anyway (no disk saving)

**Classification: REGENERABLE — KEEP**

---

## COMPLETE FILE CLASSIFICATION TABLE

| Category | Path | Reason | Risk |
|----------|------|--------|------|
| NEVER DELETE | `IBM Data Science Professional Certificate.zip` | Source of truth for all data | CATASTROPHIC |
| NEVER DELETE | `database/schema.sql` | DB blueprint | CRITICAL |
| NEVER DELETE | `.env` | Live DB credentials | CRITICAL |
| KEEP — Code | `preprocessing/run_pipeline.py` | Master pipeline runner | HIGH |
| KEEP — Code | `preprocessing/extract_course.py` | ZIP extraction | HIGH |
| KEEP — Code | `preprocessing/load_to_db.py` | DB ingestion | HIGH |
| KEEP — Code | `preprocessing/common/*.py` (5 files) | Core utilities | HIGH |
| KEEP — Code | `preprocessing/transcript/process_srt.py` | SRT processor | HIGH |
| KEEP — Code | `preprocessing/transcript/process_txt.py` | TXT processor | HIGH |
| KEEP — Code | `preprocessing/html_proc/process_html.py` | HTML processor | HIGH |
| KEEP — Code | `preprocessing/video/process_videos.py` | Video processor | MEDIUM |
| KEEP — Code | `preprocessing/assignment/process_assignment.py` | Assignment processor | MEDIUM |
| KEEP — Code | `preprocessing/quality/run_quality_checks.py` | DQ checks | HIGH |
| KEEP — Code | `database/init_db.py` | Schema initializer | HIGH |
| KEEP — Code | `database/setup_db.sql` | DB setup SQL | MEDIUM |
| KEEP — Code | `database/migrations/001_add_rag_embedding_columns.sql` | AI/RAG migration | HIGH |
| KEEP — Code | `tests/conftest.py` | Test fixtures | HIGH |
| KEEP — Code | `tests/test_*.py` (4 files) | 93 tests | HIGH |
| KEEP — Docs | `docs/course_structure.md` | Phase 1 reference | MEDIUM |
| KEEP — Docs | `docs/asset_relationships.md` | Architecture reference | MEDIUM |
| KEEP — Docs | `docs/data_quality_report.md` | Historical DQ record | LOW |
| KEEP — Docs | `docs/database_design.md` | Schema rationale | MEDIUM |
| KEEP — Docs | `docs/phase3_database_validation_report.md` | Phase 3 sign-off | HIGH |
| KEEP — Docs | `docs/ai_rag_data_contract.md` | AI/RAG handoff | CRITICAL |
| KEEP — Docs | `docs/sample_rag_records.json` | AI/RAG sample data | HIGH |
| KEEP — Config | `.env.example` | Team onboarding template | MEDIUM |
| KEEP — Config | `.gitignore` | Prevents credential commits | MEDIUM |
| KEEP — Config | `requirements.txt` | Package dependencies | HIGH |
| KEEP — Config | `pytest.ini` | Test configuration | HIGH |
| KEEP — Config | `README.md` | Project overview | MEDIUM |
| KEEP — Data | `data/raw/` (157 files) | Active working dataset (regenerable) | MEDIUM |
| KEEP — Data | `data/inventory/course_inventory.json` | Pipeline input for load_to_db | HIGH |
| KEEP — Data | `data/processed/images/` (3 PNG) | Referenced by DB readings table | MEDIUM |
| REVIEW | `database/generate_sample_rag.py` | Sample generator tool | LOW |
| REVIEW | `database/validate_phase3.py` | DB validation tool | LOW |
| REVIEW | `docs/phase3_raw_validation.json` | Machine-readable validation snapshot | LOW |
| REVIEW | `logs/pipeline.log` | Last pipeline run log (garbled) | NONE |
| SAFE TO DELETE | `preprocessing/__pycache__/` | Python bytecode cache | NONE |
| SAFE TO DELETE | `preprocessing/common/__pycache__/` | Python bytecode cache | NONE |
| SAFE TO DELETE | `preprocessing/html_proc/__pycache__/` | Python bytecode cache | NONE |
| SAFE TO DELETE | `preprocessing/quality/__pycache__/` | Python bytecode cache | NONE |
| SAFE TO DELETE | `preprocessing/transcript/__pycache__/` | Python bytecode cache | NONE |
| SAFE TO DELETE | `tests/__pycache__/` | pytest bytecode cache | NONE |
| SAFE TO DELETE | `.pytest_cache/` | pytest run cache | NONE |
| SAFE TO DELETE | `docs/phase2_validation_report.md` | Auto-generated by pipeline every run; superseded by phase3 report; contains garbled encoding | NONE |
