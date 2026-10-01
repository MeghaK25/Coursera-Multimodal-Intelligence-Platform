class EvidenceValidator:
    def validate(self, result: dict, retrieved_evidence: list[dict]) -> dict:
        if not isinstance(result, dict):
            raise ValueError("RAG result must be a dictionary.")

        if "answer" not in result:
            raise ValueError("RAG result is missing 'answer'.")

        if "evidence_ids" not in result:
            raise ValueError("RAG result is missing 'evidence_ids'.")

        if "confidence" not in result:
            raise ValueError("RAG result is missing 'confidence'.")

        if not isinstance(result["evidence_ids"], list):
            raise ValueError("'evidence_ids' must be a list.")

        confidence = result["confidence"]

        if not isinstance(confidence, (int, float)):
            raise ValueError("'confidence' must be a number.")

        if not 0.0 <= confidence <= 1.0:
            raise ValueError("'confidence' must be between 0 and 1.")

        # Only citation IDs such as E1, E2, E3 are exposed to the LLM.
        valid_citation_ids = {
            item["citation_id"]
            for item in retrieved_evidence
        }

        invalid_ids = [
            evidence_id
            for evidence_id in result["evidence_ids"]
            if evidence_id not in valid_citation_ids
        ]

        if invalid_ids:
            raise ValueError(
                f"LLM referenced invalid evidence IDs: {invalid_ids}"
            )

        return result