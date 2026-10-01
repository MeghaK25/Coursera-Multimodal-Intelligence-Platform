def clean_text(text: str) -> str:
    """Normalize line breaks and repeated whitespace."""
    return " ".join(text.replace("\n", " ").split())

def create_chunks(text: str, chunk_size: int = 500, overlap: int = 50):
    """Split long content into overlapping chunks for embedding/RAG."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    text = clean_text(text)
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap

    return chunks
