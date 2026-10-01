from AI_RAG.llm.model import GeminiModel
from AI_RAG.llm.synthesizer import Synthesizer


model = GeminiModel()
synthesizer = Synthesizer(model)

prompt = """
Answer the following question using only the provided evidence.

Question:
What is data science?

Evidence:
Data science is the study and analysis of data to discover insights,
patterns, and useful information.

Return ONLY valid JSON in this format:

{
    "answer": "your answer",
    "evidence_ids": ["test-evidence-1"],
    "confidence": 0.9
}
"""

result = synthesizer.generate(prompt)

print("\n===== SYNTHESIZER RESULT =====\n")
print(result)

print("\n===== RESULT TYPE =====\n")
print(type(result))