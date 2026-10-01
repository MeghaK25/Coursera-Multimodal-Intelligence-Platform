# RAG & LLM Pipeline

**Project:** Coursera Multimodal Intelligence Platform
**Component:** Retrieval-Augmented Generation (RAG) & LLM
**Owner:** Person 5
**Status:** MVP implementation complete and tested

---

## 1. Overview

The `rag` module provides the **Retrieval-Augmented Generation (RAG) layer** of the Coursera Multimodal Intelligence Platform.

It takes a user's question, retrieves relevant learning content from the vector database, sends the retrieved evidence to an LLM, and returns a grounded answer with supporting evidence and confidence information.

### Core flow

```text
User Question
     ↓
Query Embedding
     ↓
Vector Search
     ↓
Relevant Course Evidence
     ↓
Similarity Threshold
     ↓
RAG Prompt
     ↓
Gemini LLM
     ↓
Structured Response
     ↓
Evidence Validation
     ↓
Grounded Answer + Citations
```

The module is designed so that the backend can call the RAG pipeline without directly managing embeddings, vector search, prompts, or the LLM.

---

# 2. Current Implementation Status

The following functionality is implemented and tested:

* Semantic embedding generation
* PostgreSQL + pgvector storage
* Cosine similarity retrieval
* Top-K evidence retrieval
* Similarity threshold filtering
* RAG prompt construction
* Gemini LLM integration
* Structured JSON output
* Evidence/citation validation
* Out-of-scope question handling
* End-to-end RAG pipeline
* Invalid evidence ID rejection
* Multi-case testing

The current implementation is ready for backend API integration and frontend consumption.

---

# 3. Technology Stack

| Component            | Technology                               |
| -------------------- | ---------------------------------------- |
| Embedding model      | `sentence-transformers/all-MiniLM-L6-v2` |
| Embedding dimensions | 384                                      |
| Vector database      | PostgreSQL + pgvector                    |
| Similarity metric    | Cosine similarity                        |
| Vector index         | HNSW                                     |
| LLM                  | Gemini 3.6 Flash                         |
| Retrieval Top-K      | 5                                        |
| Minimum similarity   | 0.40                                     |

---

# 4. Project Structure

```text
rag/
│
├── __init__.py
├── pipeline.py
│
├── embedding/
│   ├── __init__.py
│   ├── embedder.py
│   ├── data_loader.py
│   └── store_embeddings.py
│
├── retrieval/
│   ├── __init__.py
│   └── retriever.py
│
├── llm/
│   ├── __init__.py
│   ├── prompts.py
│   ├── model.py
│   ├── synthesizer.py
│   └── evidence_validator.py
│
└── migrations/
    └── setup_embeddings.sql
```

---

# 5. Module Responsibilities

## `pipeline.py`

Main entry point for the RAG system.

It coordinates:

1. Retrieval
2. Evidence filtering
3. Prompt construction
4. LLM generation
5. Evidence validation
6. Final response creation

---

## `embedding/`

Responsible for:

* Loading processed learning content
* Generating embeddings
* Preparing embedding data
* Storing vectors in PostgreSQL

---

## `retrieval/`

Responsible for:

* Converting a question into an embedding
* Searching pgvector
* Ranking evidence by similarity
* Returning source information and citation IDs

---

## `llm/`

Contains the LLM-related components:

* `prompts.py` — RAG prompt construction
* `model.py` — Gemini API integration
* `synthesizer.py` — JSON response parsing and validation
* `evidence_validator.py` — evidence ID and confidence validation

---

## `migrations/`

Contains the database migration required for storing embeddings.

---

# 6. Database Requirements

The RAG module uses PostgreSQL with the `pgvector` extension.

The following embedding fields are used:

### `transcript_segments`

```text
embedding_model
embedding VECTOR(384)
```

### `readings`

```text
embedding_model
embedding VECTOR(384)
```

HNSW indexes are used for vector similarity search.

The migration is located at:

```text
rag/migrations/setup_embeddings.sql
```

---

# 7. Current Knowledge Base

The current MVP knowledge base contains processed course content including transcripts and readings.

Current embedding corpus:

* 102 semantic transcript chunks
* 19 RAG-enabled readings
* 121 total embedding records

The underlying processed dataset currently contains:

* 1 course
* 4 modules
* 12 groups
* 65 lessons
* 157 assets
* 90 transcripts
* 3,382 transcript segments
* 22 readings

The current retrieval implementation is primarily text-based.

---

# 8. Configuration

The Gemini API key must be provided through an environment variable:

```text
GEMINI_API_KEY
```

Example:

```text
GEMINI_API_KEY=<your-api-key>
```

Do **not** hardcode the API key in source code or commit it to the repository.

The LLM configuration is contained in:

```text
rag/llm/model.py
```

---

# 9. Using the RAG Pipeline

The backend should use `RAGPipeline` as the main integration interface.

```python
from rag.pipeline import RAGPipeline

pipeline = RAGPipeline(
    top_k=5,
    min_similarity=0.40
)

result = pipeline.answer(
    "What is data science?"
)
```

The backend does not need to directly call the embedding model, pgvector, Gemini, or the prompt builder.

---

# 10. Response Format

A successful response has the following structure:

```json
{
  "answer": "Data science is ...",
  "evidence_ids": ["E1", "E3"],
  "confidence": 0.95,
  "retrieval_score": 0.7481,
  "evidence": [
    {
      "citation_id": "E1",
      "evidence_id": "database-uuid",
      "asset_id": "asset-uuid",
      "similarity": 0.7481,
      "source_type": "transcript",
      "text": "Relevant course content..."
    }
  ]
}
```

### Response fields

| Field             | Description                                       |
| ----------------- | ------------------------------------------------- |
| `answer`          | Final grounded answer                             |
| `evidence_ids`    | Evidence references selected by the LLM           |
| `confidence`      | LLM-generated value between 0 and 1               |
| `retrieval_score` | Highest similarity score among retrieved evidence |
| `evidence`        | Retrieved source material                         |
| `citation_id`     | Short user-facing citation such as `E1`           |
| `evidence_id`     | Internal database identifier                      |
| `asset_id`        | Related learning asset                            |
| `similarity`      | Similarity score for the evidence                 |
| `source_type`     | Type of source                                    |

---

# 11. Citation IDs vs Evidence IDs

These identifiers have different purposes.

### Citation ID

Example:

```text
E1
```

Use this for frontend/user-facing citations.

### Evidence ID

Example:

```text
550e8400-e29b-41d4-a716-446655440000
```

This is the internal database identifier and should be retained for tracing and source lookup.

Do not replace the internal UUID with the citation ID.

---

# 12. Relevance Filtering

The pipeline uses:

```text
min_similarity = 0.40
```

If the retrieved evidence does not meet this threshold, the system does not ask Gemini to generate an unsupported answer.

Instead, it returns:

```text
The available course evidence is insufficient to answer this question.
```

For example:

```text
"What is data science?"
→ Relevant evidence
→ Answer generated
```

```text
"What is the capital of France?"
→ Very low similarity
→ Evidence rejected
→ Insufficient-evidence response
```

This is an important grounding mechanism.

---

# 13. LLM Output Validation

Gemini is instructed to return:

```json
{
  "answer": "Your answer",
  "evidence_ids": ["E1", "E2"],
  "confidence": 0.95
}
```

The response is validated before being returned by the pipeline.

Validation checks include:

* Required fields are present
* `answer` is a string
* `evidence_ids` is a list
* `confidence` is numeric
* Confidence is between `0` and `1`
* Every referenced evidence ID exists in the retrieved evidence

Invalid evidence references are rejected.

---

# 14. Backend Integration

The backend can expose the RAG functionality through the project's existing API.

Example:

```text
POST /api/ask
```

Request:

```json
{
  "question": "What is data science?"
}
```

The backend should:

```text
Receive question
      ↓
Validate request
      ↓
pipeline.answer(question)
      ↓
Return RAG response
```

The exact API route can follow the project's existing backend conventions.

---

# 15. Frontend Integration

The frontend should consume the backend response rather than interacting directly with the RAG implementation.

Primary fields:

```text
answer
evidence_ids
evidence
confidence
```

Recommended display:

```text
Answer
────────────────────────
Data science is ...

Sources: [E1] [E3]

Evidence
────────────────────────
E1
Relevant transcript content...

E3
Relevant course content...
```

The evidence section can be expandable/collapsible.

The frontend does not need to know about:

* embeddings
* PostgreSQL
* pgvector
* Gemini
* prompts
* vector similarity calculations

---

# 16. Testing

The RAG implementation has been tested with:

### Relevant questions

```text
What is data science and what skills are important for a data scientist?

What is the role of data visualization in data science?

How do data scientists use machine learning?
```

These produced grounded answers with evidence IDs.

### Out-of-scope question

```text
What is the capital of France?
```

The system correctly returned an insufficient-evidence response rather than generating an unsupported answer.

### Validation tests

The following have also been verified:

```text
✓ Retrieval
✓ Similarity threshold
✓ Gemini generation
✓ JSON parsing
✓ Evidence validation
✓ Invalid evidence rejection
✓ End-to-end RAG flow
```

---

# 17. Current Limitations

The current MVP has the following limitations:

* Retrieval is primarily text-based.
* The current corpus is limited to the processed MVP course content.
* Video-specific retrieval is not currently part of this pipeline.
* Timestamp-level video citations are not yet implemented.
* Confidence is an LLM-generated signal and is not a calibrated probability.
* The `0.40` threshold was evaluated against the current corpus and may require reevaluation for substantially different datasets.

---

# 18. Future Enhancements

Potential future improvements include:

* Full multimodal retrieval
* Video timestamp citations
* PDF/page-level citations
* Slide-level citations
* Quiz and discussion retrieval
* Hybrid keyword + vector search
* Retrieval reranking
* Metadata filtering
* Improved source metadata
* Retrieval evaluation
* Grounding evaluation
* Latency monitoring

These are outside the current MVP integration requirement.

---

# 19. Integration Rules

During backend/frontend integration:

### Use

```python
pipeline.answer(question)
```

as the primary RAG interface.

### Do not duplicate

* Embedding generation
* Vector retrieval
* RAG prompting
* Gemini integration
* Evidence validation

### Keep

```text
top_k = 5
min_similarity = 0.40
```

during the initial integration unless changes are agreed after evaluation.

---

# 20. Status

### Completed

```text
✓ Embedding pipeline
✓ Vector storage
✓ Semantic retrieval
✓ RAG pipeline
✓ Gemini integration
✓ Prompt construction
✓ Structured LLM output
✓ Evidence validation
✓ Similarity threshold
✓ Out-of-scope handling
✓ End-to-end testing
```

### Next

```text
Backend
→ Expose RAGPipeline through the API

Frontend
→ Display answer, citations and evidence

Future
→ Extend toward full multimodal retrieval
```

---

## Quick Reference

```python
from rag.pipeline import RAGPipeline

pipeline = RAGPipeline(
    top_k=5,
    min_similarity=0.40
)

result = pipeline.answer(question)
```

**Primary integration point:** `rag.pipeline.RAGPipeline`

**LLM:** Gemini 3.6 Flash

**Embedding model:** `all-MiniLM-L6-v2`

**Vector database:** PostgreSQL + pgvector

**Embedding dimension:** 384

**Default Top-K:** 5

**Minimum similarity:** 0.40

**API key:** `GEMINI_API_KEY`

For detailed integration instructions, testing information, ownership, and handoff requirements, see **`HANDOFF.md`**.
