from AI_RAG.retrieval.retriever import Retriever
from AI_RAG.llm.prompts import build_rag_prompt
from AI_RAG.llm.model import GeminiModel
from AI_RAG.llm.synthesizer import Synthesizer
from AI_RAG.llm.evidence_validator import EvidenceValidator


class RAGPipeline:
    def __init__(
        self,
        top_k: int = 5,
        min_similarity: float = 0.40
    ):
        self.retriever = Retriever()

        self.llm = GeminiModel()
        self.synthesizer = Synthesizer(self.llm)
        self.validator = EvidenceValidator()

        self.top_k = top_k
        self.min_similarity = min_similarity

    def answer(self, question: str):
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        # Step 1: Retrieve relevant evidence
        evidence = self.retriever.search(
            question,
            top_k=self.top_k
        )

        if not evidence:
            return {
                "answer": "No relevant evidence was found.",
                "evidence_ids": [],
                "confidence": 0.0,
                "retrieval_score": 0.0,
                "evidence": []
            }

        # Step 2: Check whether the retrieved evidence
        # is sufficiently relevant to the question.
        max_similarity = max(
            item["similarity"]
            for item in evidence
        )

        if max_similarity < self.min_similarity:
            return {
                "answer": (
                    "The available course evidence is insufficient "
                    "to answer this question."
                ),
                "evidence_ids": [],
                "confidence": 0.0,
                "retrieval_score": max_similarity,
                "evidence": []
            }

        # Step 3: Build RAG prompt
        prompt = build_rag_prompt(
            question,
            evidence
        )

        # Step 4: Generate response and validate grounding
        try:
            result = self.synthesizer.generate(prompt)

            validated_result = self.validator.validate(
                result,
                evidence
            )

        except Exception as exc:
            return {
                "answer": (
                    "The AI service was unable to generate a "
                    "grounded answer. Please try again."
                ),
                "evidence_ids": [],
                "confidence": 0.0,
                "retrieval_score": max_similarity,
                "evidence": [],
                "error": str(exc)
            }

        # Step 5: Return validated RAG response
        return {
            "answer": validated_result["answer"],
            "evidence_ids": validated_result["evidence_ids"],
            "confidence": validated_result["confidence"],
            "retrieval_score": max_similarity,
            "evidence": evidence
        }