from AI_RAG.retrieval.retriever import Retriever


MIN_SIMILARITY = 0.40

retriever = Retriever()

questions = [
    (
        "What is data science and what skills are important for a data scientist?",
        True
    ),
    (
        "What is the role of data visualization in data science?",
        True
    ),
    (
        "How do data scientists use machine learning?",
        True
    ),
    (
        "What is the capital of France?",
        False
    )
]


for question, should_have_evidence in questions:

    print("\n" + "=" * 80)
    print("QUESTION:", question)

    evidence = retriever.search(
        question,
        top_k=5
    )

    if not evidence:
        max_similarity = 0.0
    else:
        max_similarity = max(
            item["similarity"]
            for item in evidence
        )

    passed_threshold = max_similarity >= MIN_SIMILARITY

    print("Top similarity:", round(max_similarity, 4))
    print("Threshold:", MIN_SIMILARITY)
    print("Passed threshold:", passed_threshold)

    if should_have_evidence:
        if passed_threshold:
            print("RESULT: PASS - relevant question accepted")
        else:
            print("RESULT: FAIL - relevant question was rejected")
    else:
        if not passed_threshold:
            print("RESULT: PASS - irrelevant question rejected")
        else:
            print("RESULT: FAIL - irrelevant question was accepted")


print("\n" + "=" * 80)
print("THRESHOLD TEST COMPLETE")
print("=" * 80)