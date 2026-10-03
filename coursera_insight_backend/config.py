import os
from dotenv import load_dotenv

# Load configuration values from a local .env file.
load_dotenv()

_raw_db_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/coursera_platform",
)
if _raw_db_url.startswith("postgresql://"):
    DATABASE_URL = _raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
else:
    DATABASE_URL = _raw_db_url
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
