from AI_RAG.llm.evidence_validator import EvidenceValidator

def test_evidence_validation():
    validator = EvidenceValidator()

    # Fixed: Changed "evidence_id" to "citation_id"
    retrieved_evidence = [
        {
            "citation_id": "evidence-1",
            "text": "Data science uses data to discover useful insights."
        },
        {
            "citation_id": "evidence-2",
            "text": "Python is commonly used for data science."
        }
    ]

    result = {
        "answer": "Data science uses data to discover useful insights.",
        "evidence_ids": ["evidence-1"],
        "confidence": 0.9
    }

    validated = validator.validate(
        result,
        retrieved_evidence
    )

    # Added an assertion so Pytest knows the test succeeded
    assert validated is not None

    print("\n===== VALIDATION RESULT =====\n")
    print(validated)
    print("\n===== VALIDATION PASSED =====")