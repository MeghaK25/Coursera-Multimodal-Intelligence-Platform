from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_URL

# SQLAlchemy engine manages connections to PostgreSQL.
engine = create_engine(DATABASE_URL)

# A new SessionLocal object is used for each API request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All database models inherit from Base.
Base = declarative_base()

def get_db():
    """Provide a database session and always close it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
