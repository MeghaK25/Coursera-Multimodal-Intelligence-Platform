from dotenv import load_dotenv
load_dotenv()
from AI_RAG.pipeline import RAGPipeline

# Dropping similarity to 0.0 to expose the raw pgvector scores
pipeline = RAGPipeline(
    top_k=5,
    min_similarity=0.0
)

# Reverting to the IBM Data Science questions
questions = [
    "What is data science and what skills are important for a data scientist?",
    "What is the role of data visualization in data science?"
]

for question in questions:

    print("\n" + "=" * 80)
    print("QUESTION:")
    print(question)
    print("=" * 80)

    result = pipeline.answer(question)

    print("\nANSWER:")
    print(result["answer"])

    print("\nEVIDENCE IDS:")
    print(result["evidence_ids"])

    print("\nCONFIDENCE:")
    print(result["confidence"])

    print("\nSIMILARITIES:")

    for evidence in result["evidence"]:
        print(
            evidence["citation_id"],
            "->",
            round(evidence["similarity"], 4)
        )

    print()