from AI_RAG.llm.evidence_validator import EvidenceValidator


validator = EvidenceValidator()

retrieved_evidence = [
    {
        "citation_id": "E1",
        "evidence_id": "evidence-1",
        "text": "Data science uses data to discover useful insights."
    },
    {
        "citation_id": "E2",
        "evidence_id": "evidence-2",
        "text": "Python is commonly used for data science."
    }
]

result = {
    "answer": "Data science uses data to discover useful insights.",
    "evidence_ids": ["fake-evidence-999"],
    "confidence": 0.9
}

try:
    validator.validate(
        result,
        retrieved_evidence
    )

    print("ERROR: Invalid evidence ID was accepted.")

except ValueError as error:
    print("\n===== INVALID EVIDENCE TEST =====\n")
    print("Validation correctly rejected the response.")
    print("Error:", error)