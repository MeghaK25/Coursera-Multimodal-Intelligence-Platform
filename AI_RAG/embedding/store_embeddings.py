from sentence_transformers import SentenceTransformer
from pgvector.psycopg import register_vector
from preprocessing.common.db import get_db

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def store_txt_embeddings(conn, model):
    query = """
        SELECT id, text
        FROM transcript_segments
        WHERE chunk_type = 'txt_window'
          AND text IS NOT NULL
          AND TRIM(text) <> ''
          AND embedding IS NULL
        ORDER BY id;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    print(f"TXT chunks to embed: {len(rows)}")

    if not rows:
        return 0

    texts = [row[1] for row in rows]
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    with conn.cursor() as cur:
        for (row_id, _), embedding in zip(rows, embeddings):
            cur.execute(
                """
                UPDATE transcript_segments
                SET embedding = %s,
                    embedding_model = %s
                WHERE id = %s;
                """,
                (embedding.tolist(), MODEL_NAME, row_id)
            )

    return len(rows)


def store_reading_embeddings(conn, model):
    query = """
        SELECT r.id, r.extracted_text
        FROM readings r
        JOIN assets a ON a.id = r.id
        WHERE a.rag_enabled = TRUE
          AND r.extracted_text IS NOT NULL
          AND TRIM(r.extracted_text) <> ''
          AND r.embedding IS NULL
        ORDER BY r.id;
    """

    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()

    print(f"Readings to embed: {len(rows)}")

    if not rows:
        return 0

    texts = [row[1] for row in rows]
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    with conn.cursor() as cur:
        for (row_id, _), embedding in zip(rows, embeddings):
            cur.execute(
                """
                UPDATE readings
                SET embedding = %s,
                    embedding_model = %s
                WHERE id = %s;
                """,
                (embedding.tolist(), MODEL_NAME, row_id)
            )

    return len(rows)


def main():
    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    with get_db() as conn:
        register_vector(conn)

        txt_count = store_txt_embeddings(conn, model)
        reading_count = store_reading_embeddings(conn, model)

        conn.commit()

    print()
    print("Embedding complete.")
    print(f"TXT embeddings stored: {txt_count}")
    print(f"Reading embeddings stored: {reading_count}")
    print(f"Total embeddings stored: {txt_count + reading_count}")


if __name__ == "__main__":
    main()