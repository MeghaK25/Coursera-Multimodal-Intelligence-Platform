import pytest
from unittest.mock import MagicMock
from AI_RAG.pipeline import RAGPipeline

def test_irrelevant_query_rejection():
    """Verify that off-topic / irrelevant queries are rejected with zero hallucinations."""
    # Mock retriever to avoid loading heavy torch models in fast unit test
    mock_retriever = MagicMock()
    mock_retriever.search.return_value = []
    
    pipeline = RAGPipeline.__new__(RAGPipeline)
    pipeline.retriever = mock_retriever
    pipeline.top_k = 5
    pipeline.min_similarity = 0.40
    pipeline.synthesizer = MagicMock()
    pipeline.validator = MagicMock()
    
    irrelevant_questions = [
        "where is taliban",
        "who is the president of france",
        "recipe for pizza",
        "who won the world cup"
    ]
    
    for q in irrelevant_questions:
        res = pipeline.answer(q, course_title="Google Data Analytics")
        assert "outside the scope" in res["answer"].lower() or "insufficient" in res["answer"].lower(), \
            f"Expected out-of-scope rejection for: '{q}', got: {res['answer']}"
        assert res["confidence"] == 0.0, f"Expected confidence 0.0 for '{q}', got: {res['confidence']}"
        assert len(res["evidence_ids"]) == 0, f"Expected 0 evidence IDs for '{q}', got: {res['evidence_ids']}"
        assert len(res["evidence"]) == 0, f"Expected 0 evidence items for '{q}', got: {res['evidence']}"

if __name__ == "__main__":
    test_irrelevant_query_rejection()
    print("Relevance guardrail tests passed successfully!")
