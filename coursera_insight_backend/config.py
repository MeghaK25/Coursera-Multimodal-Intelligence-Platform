import os
from dotenv import load_dotenv

# Load configuration values from a local .env file.
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/coursera_platform",
)
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
