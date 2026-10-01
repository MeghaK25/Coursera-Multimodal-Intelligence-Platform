from services.embedding_service import create_embedding
from services.qdrant_service import search_course

def retrieve_context(question: str, course_id: int):
    """Embed a question and retrieve the most semantically similar course chunks."""
    question_vector = create_embedding(question)
    results = search_course(question_vector, course_id)

    return [
        {
            "text": point.payload.get("text", ""),
            "asset_id": point.payload.get("asset_id"),
            "segment_id": point.payload.get("segment_id"),
            "start_time": point.payload.get("start_time"),
            "end_time": point.payload.get("end_time"),
            "score": point.score,
        }
        for point in results
    ]
