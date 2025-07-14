import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL", "postgresql://user:password@localhost:5432/calif")

# SQLAlchemy engine
engine = create_engine(
    POSTGRES_DB_URL,
    # connect_args={"check_same_thread": False} # This is for SQLite only
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for SQLAlchemy models
Base = declarative_base()

# Export text for raw queries
__all__ = ["engine", "SessionLocal", "Base", "text"] 