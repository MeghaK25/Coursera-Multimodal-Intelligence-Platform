# Coursera Insight Backend

A commented starter backend for the UI/architecture supplied for the Coursera course-analysis project.

## Architecture

Admin / Frontend -> FastAPI -> PostgreSQL -> Embeddings -> Qdrant -> RAG Retrieval -> LLM -> Analysis / Evidence / AI Chat

PostgreSQL is the structured source of truth. Qdrant stores semantic vectors. The LLM receives retrieved course evidence instead of being asked to answer only from general knowledge.

## Main database entities

- Course
- Module
- Lesson
- Asset
- Transcript
- Segment
- Reading
- ProcessingJob
- DQIssue

## Setup

1. Install PostgreSQL and create a database named `coursera_insight`.
2. Run Qdrant locally (or configure a Qdrant server).
3. Copy `.env.example` to `.env` and fill in your credentials.
4. Create a Python virtual environment.
5. Install dependencies:

    pip install -r requirements.txt

6. Start the API:

    uvicorn main:app --reload

7. Open `/docs` on the local API address to test the endpoints in Swagger.

## UI -> API mapping

- Dashboard: `GET /analysis/dashboard`
- Add Course: `POST /courses/analyze`
- Processing Screen: `GET /courses/{course_id}/status`
- Analysis Results: `GET /analysis/{course_id}`
- AI Chat: `POST /chat/`

## Important project note

This starter registers a course URL but intentionally does not implement unauthorized scraping of Coursera. The ingestion layer should process course data/files that your project is authorized to access, such as supplied SRT, TXT and HTML assets.

## How to explain RAG

1. Course text is cleaned and split into smaller segments.
2. Each RAG-eligible segment is converted to an embedding.
3. The vector and source metadata are stored in Qdrant.
4. A user's question is also converted to an embedding.
5. Qdrant searches only segments belonging to the selected course.
6. The best segments are passed to the LLM as evidence.
7. The LLM generates a grounded answer and the API also returns the source metadata for an Evidence page.

## Production improvements

For a production deployment add background workers for ingestion, Alembic migrations, full JWT login routes, role-based authorization, structured logging, rate limiting, tests, stricter CORS, secret management, and richer analysis/recommendation tables.
