# Coursera Multimodal Intelligence Platform

An evidence-first data and AI platform designed to transform authorized Coursera course archives into clean, structured, validated, and RAG-ready knowledge bases. 

While architected to ingest and support **any course archive**, the platform has been end-to-end validated and benchmarked using the **IBM Data Science Professional Certificate** course dataset.

---

## Team & Contributions

### Database & Preprocessing
* **Chetan Kailas Patil** — [GitHub](https://github.com/Chetanpatil71502/)
* **Sona Christina A T** — [Email](mailto:sonachristina15@gmail.com)

### Backend (API & Orchestration)
* **Tushar** — [Email](mailto:tushar.10012003@gmail.com)
* **Gaurav Jagannath Kadam** — [GitHub](https://github.com/Gaurav0358)

### AI / RAG
* **Sakshi Kumari** — [GitHub](https://github.com/SakshiBhardwaj27)
* **Megha Mahesh Kanavi** — [Email](mailto:meghakanavi.uk@gmail.com)

### Frontend
* **P Sankarshan** — [GitHub](https://github.com/sankarshan07)

### Testing, Integration & Deployment
* **Abhishek Kumar** — [GitHub](https://github.com/abhik99)

---

## Validation Dataset

* **Course**: IBM Data Science Professional Certificate (Used for benchmark testing and pipeline validation)
* **Format**: Authorized local sample course archive (`.zip`)
* **Integrity**: The original course archive serves as the immutable source of truth and is never modified by the ingestion pipeline.

---

## Project Overview

The platform is designed to process multimodal course content such as:

* Video
* SRT transcripts
* TXT transcripts
* HTML readings
* Assignments
* Embedded images
* Course metadata

The current implementation focuses on the **Database & Data Preprocessing layer**.

The processed data is stored in PostgreSQL and prepared for the AI/RAG team.

### Overall Architecture

```text
Authorized Course Dataset
          │
          ▼
     Data Ingestion
          │
          ▼
    Data Preprocessing
    ┌─────┼─────┐
    ▼     ▼     ▼
  Video  SRT   TXT
          │
          ▼
         HTML
          │
          ▼
    Data Quality Checks
          │
          ▼
      PostgreSQL
          │
          ▼
    RAG-Ready Dataset
          │
          ▼
      AI / RAG Layer
          │
          ▼
 Embeddings → Vector DB → RAG → LLM
```

---

# Project Status

## Database & Data Preprocessing

**Status: Complete and validated**

The current implementation has completed:

* Dataset analysis
* Course hierarchy discovery
* PostgreSQL schema design
* Data ingestion
* SRT processing
* TXT chunking
* HTML extraction
* Data quality validation
* Database loading
* Idempotent pipeline execution
* Automated testing
* RAG metadata preparation
* AI/RAG handoff documentation

---

# Dataset

The IBM Data Science Professional Certificate dataset contains:

| Metric           | Value |
| ---------------- | ----: |
| Total files      |   157 |
| Videos           |    45 |
| SRT transcripts  |    45 |
| TXT transcripts  |    45 |
| HTML files       |    22 |
| Modules          |     4 |
| Lesson groups    |    12 |
| Lesson records   |    65 |
| Optional modules |     1 |

### Course Structure

```text
IBM Data Science Professional Certificate
│
├── Module 01: Defining Data Science and What Data Scientists Do
│   ├── Welcome To The Course
│   ├── Defining Data Science
│   └── What Do Data Scientists Do
│
├── Module 02: Data Science Topics
│   ├── Big Data And Data Mining
│   └── Deep Learning And Machine Learning
│
├── Module 03: Applications and Careers in Data Science
│   ├── Data Science Application Domains
│   ├── Careers And Recruiting
│   ├── Final Assignment
│   ├── Course Wrap Up
│   └── Digital Badge
│
└── Module 04: Data Literacy for Data Science
    ├── Understanding Data
    └── Data Literacy
```

**Module 04 is optional and is preserved in the database using `is_optional = true`.**

---

# Technology Stack

## Backend / Data

* Python 3.13.6
* PostgreSQL
* psycopg3
* Pydantic
* BeautifulSoup
* FFmpeg / ffprobe

## Testing

* pytest

## Future AI/RAG Layer

The database is designed to support:

* Embeddings
* Vector database
* Retrieval-Augmented Generation (RAG)
* LLM-based analysis
* Evidence-grounded recommendations
* Course-specific AI chatbot

The embedding model and vector dimension are intentionally not fixed in the current database schema.

---

# Database Architecture

The PostgreSQL database contains 12 tables:

```text
courses
course_modules
lesson_groups
lessons
assets
videos
video_segments
transcripts
transcript_segments
readings
processing_jobs
data_quality_issues
```

### Core Relationship

```text
Course
  │
  ├── Modules
  │     │
  │     └── Lesson Groups
  │            │
  │            └── Lessons
  │                   │
  │                   └── Assets
  │                          ├── Video
  │                          ├── Transcript
  │                          └── Reading
```

---

# Asset Registry

The `assets` table acts as the central registry for course content.

Each asset can contain metadata such as:

* Asset ID
* Lesson ID
* Asset type
* Source path
* Filename
* SHA-256 checksum
* Asset category
* Processing status
* RAG eligibility
* Created/updated timestamps

This allows processed content to remain traceable to its original source.

---

# Data Processing Pipeline

The master pipeline is:

```text
preprocessing/run_pipeline.py
```

It orchestrates the processing workflow.

### Pipeline

```text
1. Extract ZIP
       ↓
2. Load course hierarchy into PostgreSQL
       ↓
3. Process SRT transcripts
       ↓
4. Process TXT transcripts
       ↓
5. Process HTML content
       ↓
6. Process video metadata/segments
       ↓
7. Run data-quality checks
```

---

# SRT Processing

SRT transcripts provide precise caption-level timestamps.

The SRT processor:

* Parses subtitle blocks
* Validates timestamps
* Cleans caption text
* Removes formatting
* Stores transcript segments
* Preserves timestamp information
* Associates segments with their source lesson

### Validated Result

```text
45 SRT files
3,280 SRT segments
0 empty captions
0 invalid timestamps
```

SRT segments use high-confidence timestamp information.

---

# TXT Processing

TXT transcripts are used for cleaner semantic chunks.

The TXT processor:

* Reads transcript text
* Cleans the content
* Splits content at sentence boundaries
* Creates chunks targeting approximately 500 tokens
* Aligns chunks with SRT timestamps where available

### Validated Result

```text
45 TXT files
102 TXT chunks
Token range: 77–500
Average: approximately 387 tokens
102/102 timestamp aligned
```

---

# HTML Processing

The HTML processor handles Coursera HTML fragments and course content.

It supports:

* Text extraction
* `<co-content>` handling
* Embedded/base64 image extraction
* Content classification
* RAG eligibility assignment

The processor classifies HTML content into supported categories such as:

```text
lesson_overview
lesson_summary
course_syllabus
assignment
infographic
administrative
tips
other
```

### Validated Result

```text
22 HTML files
22 successfully processed
19 RAG-enabled
3 administrative assets excluded from RAG
```

---

# Data Quality

The project includes automated data-quality checks.

Quality results are stored in:

```text
data_quality_issues
```

The system validates things such as:

* Missing relationships
* Duplicate assets
* Invalid metadata
* Processing failures
* Data integrity issues

The final validated database contains:

```text
0 orphan records
0 duplicate asset slugs
0 duplicate checksums
```

---

# RAG Readiness

The database is prepared for the AI/RAG team.

Current RAG metadata:

```text
157 total assets
154 RAG-enabled assets
3 administrative assets excluded
```

The main content available for future embedding includes:

```text
3,280 SRT caption segments
102 TXT semantic chunks
22 HTML readings
```

Each content record can preserve source lineage such as:

```text
Course
 ↓
Module
 ↓
Lesson
 ↓
Asset
 ↓
Source File
 ↓
Content Segment
 ↓
Timestamp (when available)
```

This allows future AI responses to be grounded in source evidence.

---

# Idempotent Ingestion

The pipeline is designed to be safely re-run.

Running the pipeline multiple times does not create duplicate records.

Validation confirmed:

```text
3 pipeline runs
0 duplicate records created
```

This makes the ingestion process suitable for future incremental updates.

---

# Testing

The project includes automated tests for:

* SRT parsing
* TXT chunking
* HTML extraction
* Utility functions

### Test Result

```text
93 / 93 tests passed
```

Run the tests with:

```bash
pytest -q
```

---

# Project Structure

```text
Coursera/
│
├── IBM Data Science Professional Certificate.zip
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── pytest.ini
├── README.md
│
├── data/
│   ├── raw/
│   ├── processed/
│   │   └── images/
│   └── inventory/
│       └── course_inventory.json
│
├── database/
│   ├── schema.sql
│   ├── init_db.py
│   ├── setup_db.sql
│   ├── validate_phase3.py
│   └── migrations/
│       └── 001_add_rag_embedding_columns.sql
│
├── preprocessing/
│   ├── common/
│   ├── extract_course.py
│   ├── load_to_db.py
│   ├── run_pipeline.py
│   ├── transcript/
│   ├── html_proc/
│   ├── video/
│   ├── assignment/
│   └── quality/
│
├── tests/
│   ├── conftest.py
│   ├── test_srt_parser.py
│   ├── test_txt_chunker.py
│   ├── test_html_extractor.py
│   └── test_utils.py
│
├── docs/
│   ├── course_structure.md
│   ├── asset_relationships.md
│   ├── data_quality_report.md
│   ├── database_design.md
│   ├── phase3_database_validation_report.md
│   ├── ai_rag_data_contract.md
│   └── sample_rag_records.json
│
└── logs/
```

---

# Setup

## 1. Create Python environment

Python 3.13.6 is currently used by the project.

Example:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

---

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Configure the PostgreSQL connection.

Example structure:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=coursera_platform
DB_USER=coursera_user
DB_PASSWORD=your_password
```

Never commit `.env` to Git.

---

# Database Setup

Initialize the PostgreSQL schema:

```bash
python database/init_db.py
```

For a clean database reset during development:

```bash
python database/init_db.py --drop-existing
```

> `--drop-existing` is destructive. Use it only when a database reset is intentionally required.

---

# Run the Pipeline

From the project root:

```bash
python preprocessing/run_pipeline.py --skip-video
```

The pipeline will:

1. Extract course data
2. Load the course hierarchy
3. Process SRT transcripts
4. Process TXT transcripts
5. Process HTML content
6. Run quality checks
7. Store results in PostgreSQL

---

# Validation

Run the database validation suite:

```bash
python database/validate_phase3.py
```

Run the complete test suite:

```bash
pytest -q
```

Expected automated test result:

```text
93 passed
```

---

# AI/RAG Handoff

The Database & Data Preprocessing layer is now ready for the AI/RAG team.

The AI/RAG team can use:

```text
transcript_segments
readings
```

with:

```sql
WHERE rag_enabled = true
```

Before generating embeddings, the AI/RAG team can apply the migration:

```text
database/migrations/001_add_rag_embedding_columns.sql
```

The embedding model and vector dimensions should be selected by the AI/RAG implementation.

---

# Important Design Principles

## Evidence First

Processed content must remain traceable to its source.

## Reproducibility

Raw source data and processing scripts are preserved so the dataset can be rebuilt.

## Idempotency

Running the ingestion pipeline multiple times must not create duplicates.

## Data Quality

Data-quality problems are explicitly detected and recorded.

## Source Lineage

Content retains course, module, lesson, asset, source-file, and timestamp relationships where available.

## Separation of Responsibilities

The current layer prepares clean structured data.

The AI/RAG layer is responsible for:

```text
Embeddings
Vector Database
Retrieval
LLM
RAG
AI Recommendations
Chatbot
```

---

# Current Limitations

### Video Metadata / Segmentation

The 45 video files are registered as assets, but detailed video metadata and video segmentation require FFmpeg/ffprobe processing.

The transcript pipeline is already available and validated.

### Embeddings

Embeddings have intentionally not been generated in this phase.

### Vector Database

No vector database has been configured yet.

These are part of the next AI/RAG implementation phase.

---

# Documentation

Important project documentation:

| Document                                    | Purpose                   |
| ------------------------------------------- | ------------------------- |
| `docs/course_structure.md`                  | Course hierarchy          |
| `docs/asset_relationships.md`               | Asset relationships       |
| `docs/data_quality_report.md`               | Data-quality analysis     |
| `docs/database_design.md`                   | Database design           |
| `docs/phase3_database_validation_report.md` | Final database validation |
| `docs/ai_rag_data_contract.md`              | AI/RAG handoff contract   |
| `docs/sample_rag_records.json`              | Example RAG-ready records |

---

# Project Achievement

The current system transforms a raw authorized Coursera course archive into a structured PostgreSQL knowledge foundation.

```text
157 Source Files
       ↓
Data Ingestion
       ↓
Preprocessing
       ↓
Data Quality
       ↓
PostgreSQL
       ↓
3,382 Text Segments
       ↓
154 RAG-Enabled Assets
       ↓
AI/RAG Handoff
```

### Validation Summary

```text
93/93 automated tests        PASS
45/45 SRT files              PASS
3,280 SRT segments           PASS
45/45 TXT files              PASS
102 TXT chunks               PASS
22/22 HTML files             PASS
154/157 RAG-enabled          PASS
0 orphan records             PASS
0 duplicate asset slugs      PASS
0 duplicate checksums        PASS
3 pipeline runs              PASS
Original ZIP                 UNTOUCHED
```

---

# Next Phase

The next stage is the **AI/RAG layer**:

```text
PostgreSQL
    ↓
Embedding Generation
    ↓
Vector Database
    ↓
Permission-aware Retrieval
    ↓
Evidence-grounded LLM
    ↓
Recommendations
    ↓
Course-specific AI Chatbot
```

The current Database & Data Preprocessing layer provides the validated foundation for this next phase.
