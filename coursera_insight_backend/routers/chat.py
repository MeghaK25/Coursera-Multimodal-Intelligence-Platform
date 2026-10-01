from fastapi import APIRouter, HTTPException
from schemas import ChatRequest

# Import your working Gemini/pgvector pipeline
from AI_RAG.pipeline import RAGPipeline

router = APIRouter(prefix="/chat", tags=["AI Chat"])

# Initialize the pipeline (using the 0.0 threshold we proved works)
pipeline = RAGPipeline(top_k=5, min_similarity=0.0)

@router.post("/")
def chat(request: ChatRequest):
    """Answer a question using only retrieved content from pgvector."""
    try:
        # Route the frontend's question directly to LangGraph and Gemini
        result = pipeline.answer(request.question)
        
        return {
            "course_id": request.course_id,
            "question": request.question,
            "answer": result["answer"],
            "confidence": result["confidence"],
            "evidence": result["evidence"] 
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))