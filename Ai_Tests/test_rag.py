from AI_RAG.pipeline import RAGPipeline


pipeline = RAGPipeline(top_k=5)

question = "What is data science and what skills are important for a data scientist?"

result = pipeline.answer(question)

print("\n===== FINAL RAG ANSWER =====\n")

print("Answer:")
print(result["answer"])

print("\nEvidence IDs:")
for evidence_id in result["evidence_ids"]:
    print("-", evidence_id)

print("\nConfidence:")
print(result["confidence"])

print("\n===== RETRIEVED EVIDENCE =====\n")

for i, evidence in enumerate(result["evidence"], start=1):
    print(f"--- Evidence {i} ---")
    print("Evidence ID:", evidence["evidence_id"])
    print("Asset ID:", evidence["asset_id"])
    print("Similarity:", evidence["similarity"])
    print("Text:", evidence["text"][:300])
    print()
if "error" in result:
    print("ERROR:")
    print(result["error"])