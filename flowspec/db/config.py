"""Database configuration and connection management."""

import os
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()


def get_db_url() -> str:
    """Get database URL from environment or default to SQLite."""
    db_type = os.getenv("DB_TYPE", "sqlite").lower()
    
    if db_type == "postgresql" or db_type == "postgres":
        user = os.getenv("DB_USER", "marquez")
        password = os.getenv("DB_PASSWORD", "marquez")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "flowspec")
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    else:
        # Default to SQLite
        db_path = os.getenv("DB_PATH", "flowspec.db")
        return f"sqlite:///{db_path}"


def get_engine():
    """Create and return database engine."""
    db_url = get_db_url()
    connect_args = {}
    
    # SQLite requires check_same_thread=False for async operations
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    
    return create_engine(db_url, connect_args=connect_args, echo=False)


def get_session() -> Generator[Session, None, None]:
    """Get database session (dependency for FastAPI)."""
    engine = get_engine()
    with Session(engine) as session:
        yield session












