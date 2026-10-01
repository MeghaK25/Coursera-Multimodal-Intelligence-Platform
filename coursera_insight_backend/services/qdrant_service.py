from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)
from config import QDRANT_URL

COLLECTION_NAME = "course_segments"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dimension

client = QdrantClient(url=QDRANT_URL)

def ensure_collection():
    """Create the vector collection the first time the application uses it."""
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )

def store_embedding(segment_id, embedding, text, course_id, asset_id,
                    start_time=None, end_time=None):
    """Store vector plus source-lineage metadata for later evidence retrieval."""
    ensure_collection()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=segment_id,
                vector=embedding,
                payload={
                    "text": text,
                    "course_id": course_id,
                    "asset_id": asset_id,
                    "segment_id": segment_id,
                    "start_time": start_time,
                    "end_time": end_time,
                },
            )
        ],
    )

def search_course(vector, course_id: int, limit: int = 5):
    """Semantic search restricted to one course to prevent cross-course answers."""
    ensure_collection()
    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="course_id",
                    match=MatchValue(value=course_id),
                )
            ]
        ),
        limit=limit,
    )
    return result.points
