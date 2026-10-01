import sys
from pathlib import Path

# Ensure both backend directory and project root are in sys.path
_BACKEND_DIR = str(Path(__file__).resolve().parent)
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)

if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _BACKEND_DIR in sys.path:
    sys.path.remove(_BACKEND_DIR)
sys.path.insert(0, _BACKEND_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Explicitly route the imports through the backend folder
from database import Base, engine
from routers import analysis, chat, courses

# Database schema is already created and managed by database/schema.sql
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Coursera Insight API",
    description="Backend for course ingestion, analysis and course-specific RAG chat.",
    version="1.0.0",
)

# Allow a frontend running on another port/domain to call the API.
# Restrict this list to your real frontend domain in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses.router)
app.include_router(analysis.router)
app.include_router(chat.router)

@app.get("/")
def home():
    return {"message": "Coursera Insight Backend Running"}

@app.get("/health")
def health():
    return {"status": "healthy"}