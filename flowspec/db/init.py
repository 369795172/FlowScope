"""Database initialization and table creation."""

from sqlmodel import SQLModel
from flowspec.db.config import get_engine
from flowspec.models import FSDataset, FSJob, FSEdge, FSRun


def create_tables():
    """Create all database tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)


def init_db():
    """Initialize database: create all tables."""
    print("Initializing FlowScope database...")
    create_tables()
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()












