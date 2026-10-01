# RAG & LLM Pipeline — Engineering Handoff

**Project:** Coursera Multimodal Intelligence Platform
**Component:** Retrieval-Augmented Generation (RAG) & LLM
**Owner:** Person 5
**Status:** Core MVP completed and tested
**Integration:** Ready for backend and frontend integration

---

## 1. Overview

The Person 5 component converts a user's question into a **grounded answer based on course content**.

The pipeline:

```text
User Question
     ↓
Query Embedding
     ↓
Vector Retrieval
     ↓
Relevant Evidence
     ↓
Similarity Threshold
     ↓
RAG Prompt
     ↓
Gemini LLM
     ↓
Structured JSON
     ↓
Evidence Validation
     ↓
Answer + Citations + Confidence
```

The RAG component is responsible for answer generation and evidence validation.

The backend is responsible for exposing this functionality through the API, and the frontend is responsible for displaying the answer and evidence.

---

# 2. What Has Been Completed

The following work is complete:

* Embedding generation integrated
* PostgreSQL + pgvector retrieval implemented
* Semantic similarity search implemented
* RAG pipeline implemented
* Gemini LLM integration completed
* RAG prompt created
* Structured JSON output implemented
* Evidence/citation validation implemented
* Similarity threshold implemented
* Out-of-scope question handling implemented
* End-to-end RAG testing completed
* Multiple question scenarios tested
* Invalid evidence IDs tested and rejected
* Response contract defined

The complete pipeline has been successfully tested using the user's own Gemini API configuration.

---

# 3. Current Technology

| Component               | Technology                               |
| ----------------------- | ---------------------------------------- |
| Embedding model         | `sentence-transformers/all-MiniLM-L6-v2` |
| Embedding size          | 384                                      |
| Vector database         | PostgreSQL + pgvector                    |
| Similarity              | Cosine similarity                        |
| Vector index            | HNSW                                     |
| LLM                     | Gemini 3.6 Flash                         |
| RAG approach            | Retrieval-Augmented Generation           |
| Default retrieval count | 5                                        |
| Similarity threshold    | 0.40                                     |

---

# 4. Current Knowledge Corpus

The current MVP preprocessing contains:

| Data                      | Count |
| ------------------------- | ----: |
| Courses                   |     1 |
| Modules                   |     4 |
| Groups                    |    12 |
| Lessons                   |    65 |
| Assets                    |   157 |
| Transcripts               |    90 |
| Transcript segments       | 3,382 |
| Readings                  |    22 |
| Semantic text chunks      |   102 |
| RAG-enabled readings      |    19 |
| Current embedding records |   121 |

The current retrieval implementation primarily uses transcript semantic chunks and RAG-enabled reading content.

Video-specific retrieval is not part of the current MVP implementation.

---

# 5. Project Structure

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

# 6. Component Responsibilities

## Embedding

Responsible for:

* Loading processed course content
* Generating 384-dimensional embeddings
* Storing embeddings in PostgreSQL
* Preventing unnecessary duplicate embedding generation

## Retrieval

Responsible for:

* Embedding the user's question
* Searching pgvector
* Ranking evidence by similarity
* Returning relevant evidence
* Attaching citation and source metadata

## RAG Pipeline

Responsible for:

1. Receiving the question
2. Retrieving evidence
3. Checking relevance
4. Building the prompt
5. Calling Gemini
6. Parsing the response
7. Validating evidence IDs
8. Returning the final response

## Evidence Validator

Responsible for ensuring:

* Required response fields exist
* Confidence is valid
* Evidence IDs are valid
* The LLM cannot cite evidence that was not retrieved

---

# 7. Main Integration Interface

The backend should use the RAG pipeline through this interface:

```python
from rag.pipeline import RAGPipeline

pipeline = RAGPipeline(
    top_k=5,
    min_similarity=0.40
)

result = pipeline.answer(question)
```

This is the **main integration point**.

The backend does not need to directly manage:

* Embedding generation
* pgvector queries
* Gemini API calls
* RAG prompt construction
* Evidence validation

Those responsibilities are already encapsulated inside the RAG module.

---

# 8. Similarity Threshold

The current threshold is:

```text
min_similarity = 0.40
```

If the highest retrieved similarity is below this value, the pipeline does not send the question to the LLM.

It returns:

```text
The available course evidence is insufficient to answer this question.
```

Example:

```text
"What is data science?"
Similarity ≈ 0.75
→ Answer generated
```

```text
"What is the capital of France?"
Similarity ≈ 0.07
→ Evidence rejected
→ No unsupported answer generated
```

The `0.40` threshold has been tested against the current corpus and should remain unchanged during initial integration.

---

# 9. LLM Configuration

The current model is:

```text
gemini-3.6-flash
```

The API key is loaded through:

```text
GEMINI_API_KEY
```

The key must be supplied through the deployment/environment configuration.

### Do not:

* Hardcode the API key
* Commit the key to Git
* Put the key in documentation
* Share the key through source files

---

# 10. RAG Prompt Behavior

The LLM receives:

* User question
* Retrieved evidence
* Evidence IDs
* Grounding instructions
* JSON output requirements

The prompt instructs Gemini to:

1. Use only retrieved evidence.
2. Avoid unsupported facts.
3. State when evidence is insufficient.
4. Identify evidence supporting the answer.
5. Use only valid evidence IDs.
6. Return structured JSON.

---

# 11. LLM Response Format

Gemini is expected to return:

```json
{
  "answer": "Your answer here",
  "evidence_ids": ["E1", "E3"],
  "confidence": 0.95
}
```

The synthesizer validates this structure before the result reaches the final pipeline response.

---

# 12. Final Response Contract

The RAG pipeline returns:

```json
{
  "answer": "Data science is ...",
  "evidence_ids": ["E1", "E3"],
  "confidence": 0.95,
  "retrieval_score": 0.7481,
  "evidence": [
    {
      "citation_id": "E1",
      "evidence_id": "long-uuid",
      "asset_id": "long-uuid",
      "similarity": 0.7481,
      "source_type": "transcript",
      "text": "Relevant course content..."
    }
  ]
}
```

---

# 13. Response Field Reference

| Field             | Purpose                                 |
| ----------------- | --------------------------------------- |
| `answer`          | Final answer for the user               |
| `evidence_ids`    | Evidence references selected by the LLM |
| `confidence`      | LLM-generated confidence value from 0–1 |
| `retrieval_score` | Highest retrieved similarity score      |
| `evidence`        | Retrieved source material               |
| `citation_id`     | Short frontend-facing ID such as `E1`   |
| `evidence_id`     | Internal database UUID                  |
| `asset_id`        | Source learning asset ID                |
| `similarity`      | Similarity score for that evidence      |
| `source_type`     | Type of source                          |

### Important

`citation_id` and `evidence_id` serve different purposes.

Example:

```text
citation_id = E1
evidence_id = <database UUID>
```

Use `E1` for user-facing citations.

Keep the UUID for internal tracing and source identification.

---

# 14. Backend Integration

The backend should expose the RAG functionality through the project's existing API structure.

A possible endpoint:

```text
POST /api/ask
```

### Request

```json
{
  "question": "What is data science?"
}
```

### Processing

```text
API Request
    ↓
Validate question
    ↓
RAGPipeline.answer(question)
    ↓
Return RAG response
```

### Response

```json
{
  "answer": "...",
  "evidence_ids": ["E1", "E3"],
  "confidence": 0.95,
  "retrieval_score": 0.7481,
  "evidence": [...]
}
```

The exact route can follow the existing backend API conventions.

---

# 15. Backend Team — What To Do Next

### Step 1 — Import the pipeline

```python
from rag.pipeline import RAGPipeline
```

### Step 2 — Initialize it

Prefer one shared pipeline instance:

```python
pipeline = RAGPipeline(
    top_k=5,
    min_similarity=0.40
)
```

### Step 3 — Connect it to the question endpoint

The endpoint should:

* Accept the user's question
* Validate the request
* Call `pipeline.answer(question)`
* Return the resulting JSON

### Step 4 — Handle insufficient evidence

If:

```json
{
  "confidence": 0.0,
  "evidence_ids": []
}
```

return the response normally.

The frontend can display the supplied message.

### Step 5 — Handle service failures

Handle failures such as:

* Gemini unavailable
* API quota exceeded
* Database failure
* Retrieval failure
* Invalid LLM response

Do not expose raw stack traces or internal errors to the user.

---

# 16. Frontend Integration

The frontend only needs the backend response.

It does not need to know about:

* Sentence Transformers
* pgvector
* PostgreSQL queries
* Gemini
* RAG prompts
* Embedding generation

The frontend should primarily consume:

```text
answer
evidence_ids
evidence
confidence
```

---

# 17. Frontend Answer Display

Display:

```text
result.answer
```

as the main response.

Example:

```text
Data science involves using data to discover patterns,
generate insights, and support decision-making.
```

---

# 18. Citation Display

Use:

```text
result.evidence_ids
```

for user-facing citations.

Example:

```text
Data science involves analyzing data to discover insights. [E1] [E3]
```

The frontend can make citations clickable or expandable.

---

# 19. Evidence Display

Use:

```text
result.evidence
```

to display supporting content.

Suggested UI:

```text
Answer
────────────────────────
Data science is ...

Sources: [E1] [E3] [E4]

Evidence
────────────────────────
E1
Relevant transcript content...

E3
Relevant course content...
```

The evidence section can be collapsible.

---

# 20. Confidence

`confidence` is a value between `0` and `1`.

Example:

```text
0.95
```

Important:

**This is an LLM-generated confidence signal, not a calibrated probability of correctness.**

It can be used internally or displayed as an informational value depending on the product requirements.

---

# 21. Retrieval Score

`retrieval_score` represents the highest similarity among retrieved evidence.

Example:

```text
retrieval_score = 0.7481
```

It is useful for:

* Debugging
* Evaluation
* Monitoring
* Relevance analysis

It should not be interpreted as answer correctness.

---

# 22. Testing Completed

The following have been tested successfully:

```text
✓ Embedding generation
✓ Vector storage
✓ Vector similarity retrieval
✓ Retrieval ranking
✓ Similarity threshold
✓ RAG prompt generation
✓ Gemini generation
✓ JSON response parsing
✓ Evidence ID validation
✓ Invalid evidence rejection
✓ End-to-end RAG pipeline
✓ Multiple question scenarios
✓ Out-of-scope question rejection
```

---

# 23. Tested Question Types

### Relevant question

```text
What is data science and what skills are important for a data scientist?
```

Result:

```text
Answer generated
Evidence returned
Confidence returned
```

### Relevant question

```text
What is the role of data visualization in data science?
```

Result:

```text
Answer generated
Evidence returned
Confidence returned
```

### Out-of-scope question

```text
What is the capital of France?
```

Result:

```text
The available course evidence is insufficient to answer this question.
```

### Machine learning question

```text
How do data scientists use machine learning?
```

Result:

```text
Answer generated
Evidence returned
Confidence returned
```

---

# 24. Current Limitations

### Text-focused retrieval

The current RAG retrieval path is primarily text-based.

### Limited MVP corpus

Only the currently processed course material is available to retrieval.

### Video retrieval

Video-specific retrieval and timestamp citations are not yet part of the current MVP.

### Confidence calibration

The confidence value is not statistically calibrated.

### Threshold

The `0.40` threshold was evaluated against the current corpus and may need reevaluation if the dataset changes substantially.

---

# 25. Future Enhancements

Possible future improvements:

* Multimodal retrieval
* Video timestamp citations
* PDF/page-level citations
* Slide-level citations
* Quiz and discussion retrieval
* Hybrid keyword + vector retrieval
* Reranking
* Metadata filtering
* Better source metadata
* Retrieval evaluation
* Answer-grounding evaluation
* Latency monitoring

These are future enhancements and are **not required for the current handoff**.

---

# 26. What Backend/Frontend Should NOT Change

During initial integration, do not independently recreate:

```text
Embedding generation
Vector retrieval
Similarity threshold
RAG prompt
Gemini integration
Evidence validation
Response structure
```

Use the existing RAG pipeline.

If changes are required, coordinate them with the Person 5 component rather than creating a second implementation.

---

# 27. Integration Checklist

## Backend

```text
[ ] Import RAGPipeline
[ ] Initialize shared pipeline
[ ] Create/connect question endpoint
[ ] Validate incoming question
[ ] Call pipeline.answer(question)
[ ] Return defined JSON response
[ ] Handle insufficient evidence
[ ] Handle Gemini/API errors
[ ] Configure GEMINI_API_KEY securely
[ ] Test relevant question
[ ] Test unrelated question
```

## Frontend

```text
[ ] Send question to backend
[ ] Display answer
[ ] Display citations
[ ] Display/expand supporting evidence
[ ] Handle insufficient evidence
[ ] Handle API errors
[ ] Avoid exposing internal database details
```

---

# 28. Definition of Done

Integration is complete when the following flow works:

```text
User enters question
        ↓
Frontend sends question
        ↓
Backend receives question
        ↓
Backend calls RAGPipeline
        ↓
Relevant evidence retrieved
        ↓
Evidence passes threshold
        ↓
Gemini generates answer
        ↓
Evidence IDs validated
        ↓
Backend returns response
        ↓
Frontend displays answer
        ↓
Frontend displays citations/evidence
```

For an unrelated question:

```text
Question
   ↓
Low retrieval similarity
   ↓
Threshold rejection
   ↓
No unsupported LLM answer
   ↓
Insufficient-evidence response
   ↓
Frontend displays message
```

---

# 29. Final Handoff Status

**Person 5 RAG & LLM implementation: COMPLETE**

Completed:

```text
✓ Retrieval integration
✓ RAG pipeline
✓ Gemini integration
✓ Prompt engineering
✓ Structured output
✓ Evidence validation
✓ Similarity threshold
✓ Out-of-scope handling
✓ End-to-end testing
✓ Backend integration contract
✓ Frontend response contract
```

### Next ownership

**Backend team:** expose `RAGPipeline.answer()` through the project API.

**Frontend team:** consume the API response and display the answer with supporting citations/evidence.

**Future development:** extend the current MVP toward full multimodal retrieval and richer source-level citations.

---

## Primary Integration Point

```python
from rag.pipeline import RAGPipeline

pipeline = RAGPipeline(
    top_k=5,
    min_similarity=0.40
)

result = pipeline.answer(question)
```

This is the primary interface that should be used for integration.
