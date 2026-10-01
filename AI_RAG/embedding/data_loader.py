from preprocessing.common.db import get_db


def fetch_txt_windows():
    """
    Fetch TXT semantic chunks that are enabled for RAG.
    """
    query = """
        SELECT
            ts.id,
            ts.text
        FROM transcript_segments ts
        WHERE ts.chunk_type = 'txt_window'
          AND ts.text IS NOT NULL
          AND TRIM(ts.text) <> ''
        ORDER BY ts.id;
    """

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()


def fetch_readings():
    """
    Fetch RAG-enabled reading/HTML content.
    """
    query = """
        SELECT
            r.id,
            r.extracted_text
        FROM readings r
        JOIN assets a ON a.id = r.id
        WHERE a.rag_enabled = TRUE
          AND r.extracted_text IS NOT NULL
          AND TRIM(r.extracted_text) <> ''
        ORDER BY r.id;
    """

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()