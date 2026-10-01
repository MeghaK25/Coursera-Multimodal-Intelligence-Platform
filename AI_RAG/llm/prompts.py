def build_rag_prompt(question: str, evidence: list[dict]) -> str:
    context_parts = []

    for item in evidence:
        context_parts.append(
            f"""
Evidence ID: {item['citation_id']}

Content:
{item['text']}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are an AI learning assistant.

Answer the user's question using ONLY the provided evidence.

USER QUESTION:
{question}

RETRIEVED EVIDENCE:
{context}

INSTRUCTIONS:
1. Use only the retrieved evidence.
2. Do not invent facts that are not supported by the evidence.
3. If the evidence is insufficient, clearly say that the available evidence is insufficient.
4. Identify the Evidence IDs that directly support your answer.
5. Only use Evidence IDs that appear in the retrieved evidence.
6. Keep the answer clear and concise.

Return your response in this JSON format:

{{
    "answer": "Your answer here",
    "evidence_ids": ["E1", "E2"],
    "confidence": 0.0
}}
"""

    return prompt