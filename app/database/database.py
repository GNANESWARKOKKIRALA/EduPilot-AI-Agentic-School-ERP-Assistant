from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Determine connection arguments based on database type (e.g. SQLite)
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args
)

# Session factory for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class for models
Base = declarative_base()

def get_db():
    """
    Dependency to yield database sessions to FastAPI routes,
    ensuring they are properly closed after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
