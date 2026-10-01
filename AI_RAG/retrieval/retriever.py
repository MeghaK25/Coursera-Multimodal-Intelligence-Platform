from sentence_transformers import SentenceTransformer
from pgvector.psycopg import register_vector

from preprocessing.common.db import get_db


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Retriever:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def search(self, query: str, top_k: int = 5):
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        # Convert user query into an embedding
        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )

        with get_db() as conn:
            register_vector(conn)

            with conn.cursor() as cur:
                emb_list = query_embedding.tolist()
                cur.execute(
                    """
                    (
                        SELECT
                            ts.id::text,
                            ts.text,
                            a.id::text AS asset_id,
                            'transcript' AS source_type,
                            1 - (ts.embedding <=> %s::vector) AS similarity
                        FROM transcript_segments ts
                        JOIN transcripts t ON t.id = ts.transcript_id
                        JOIN assets a ON a.id = t.id
                        WHERE ts.embedding IS NOT NULL
                          AND a.rag_enabled = TRUE
                        ORDER BY ts.embedding <=> %s::vector
                        LIMIT %s
                    )
                    UNION ALL
                    (
                        SELECT
                            r.id::text,
                            r.extracted_text AS text,
                            a.id::text AS asset_id,
                            'reading' AS source_type,
                            1 - (r.embedding <=> %s::vector) AS similarity
                        FROM readings r
                        JOIN assets a ON a.id = r.id
                        WHERE r.embedding IS NOT NULL
                          AND a.rag_enabled = TRUE
                        ORDER BY r.embedding <=> %s::vector
                        LIMIT %s
                    )
                    ORDER BY similarity DESC
                    LIMIT %s;
                    """,
                    (
                        emb_list,
                        emb_list,
                        top_k,
                        emb_list,
                        emb_list,
                        top_k,
                        top_k
                    )
                )

                rows = cur.fetchall()
        results = []

        for index, row in enumerate(rows, start=1):
            results.append({
                "citation_id": f"E{index}",
                "evidence_id": str(row[0]),
                "text": row[1],
                "asset_id": str(row[2]),
                "source_type": str(row[3]),
                "similarity": float(row[4])
            })

        return results
        # results = []

        # for row in rows:
        #     results.append({
        #         "evidence_id": str(row[0]),
        #         "text": row[1],
        #         "asset_id": str(row[2]),
        #         "similarity": float(row[3])
        #     })

        # return results