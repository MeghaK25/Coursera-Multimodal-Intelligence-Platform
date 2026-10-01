from functools import lru_cache
from sentence_transformers import SentenceTransformer

@lru_cache(maxsize=1)
def get_embedding_model():
    """Load the embedding model only once instead of on every API request."""
    return SentenceTransformer("all-MiniLM-L6-v2")

def create_embedding(text: str):
    """Convert text into a numerical vector used for semantic similarity search."""
    model = get_embedding_model()
    return model.encode(text).tolist()
