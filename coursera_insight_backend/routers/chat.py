from fastapi import APIRouter, HTTPException
from schemas import ChatRequest

# Import your working Gemini/pgvector pipeline
from AI_RAG.pipeline import RAGPipeline

router = APIRouter(prefix="/chat", tags=["AI Chat"])

# Initialize the pipeline with certified 0.40 similarity threshold
pipeline = RAGPipeline(top_k=5, min_similarity=0.40)

@router.post("/")
def chat(request: ChatRequest):
    """Answer a question using only retrieved content from pgvector."""
    try:
        # Route the frontend's question with course context to pipeline
        result = pipeline.answer(request.question, course_title=request.course_title)
        
        return {
            "course_id": request.course_id,
            "question": request.question,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "evidence": result["evidence"] 
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))