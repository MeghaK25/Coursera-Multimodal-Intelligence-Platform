from openai import OpenAI
from config import OPENAI_API_KEY
from services.retrieval_service import retrieve_context

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_course(course_id: int, question: str):
    """RAG pipeline: retrieve course evidence first, then ask the LLM to answer."""
    evidence = retrieve_context(question, course_id)

    if not evidence:
        return "I could not find sufficient evidence in this course.", []

    context = "\n\n".join(
        f"[Evidence {i}] {item['text']}" for i, item in enumerate(evidence, start=1)
    )

    prompt = f"""
You are an AI course analysis assistant.

Answer the user's question using ONLY the COURSE EVIDENCE below.
Do not invent facts that are not present in the evidence.
If the evidence is insufficient, say:
"I could not find sufficient evidence in this course."

COURSE EVIDENCE:
{context}

QUESTION:
{question}
"""

    response = client.responses.create(
        model="gpt-5.6",
        input=prompt,
    )

    return response.output_text, evidence
