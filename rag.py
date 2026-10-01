import os
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

load_dotenv()

BASE_DIR = os.path.dirname(__file__)
FAISS_BASE = os.path.join(BASE_DIR, "faiss_indexes")
os.makedirs(FAISS_BASE, exist_ok=True)

def get_embeddings():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=api_key
        )
    else:
        from langchain_community.embeddings import FakeEmbeddings
        return FakeEmbeddings(size=768)

def create_course_vector_store(documents: list, course_id: int):
    folder = os.path.join(FAISS_BASE, f"course_{course_id}")
    embeddings = get_embeddings()

    db = FAISS.from_documents(documents, embeddings)
    db.save_local(folder)
    return folder

def search_course_chunks(course_id: int, query: str, k: int = 5):
    folder = os.path.join(FAISS_BASE, f"course_{course_id}")
    if not os.path.exists(folder):
        return []

    embeddings = get_embeddings()
    db = FAISS.load_local(folder, embeddings, allow_dangerous_deserialization=True)
    return db.similarity_search(query=query, k=k)
