from AI_RAG.retrieval.retriever import Retriever


retriever = Retriever()

questions = [
    "What is data science and what skills are important for a data scientist?",
    "What is the role of data visualization in data science?",
    "How do data scientists use machine learning?",
    "What is the capital of France?"
]


for question in questions:

    print("\n" + "=" * 80)
    print("QUESTION:")
    print(question)
    print("=" * 80)

    results = retriever.search(
        question,
        top_k=5
    )

    if not results:
        print("\nNO RESULTS FOUND")
        continue

    print("\nRETRIEVED EVIDENCE:")

    for evidence in results:
        print("\n---", evidence["citation_id"], "---")
        print("Evidence ID:", evidence["evidence_id"])
        print("Asset ID:", evidence["asset_id"])
        print("Source Type:", evidence["source_type"])
        print("Similarity:", round(evidence["similarity"], 4))
        print("Text:", evidence["text"][:300])