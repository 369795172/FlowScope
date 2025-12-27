"""Job model for FlowScope."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class FSJob(SQLModel, table=True):
    """Job model representing a data transformation or processing task."""

    __tablename__ = "fs_job"

    id: Optional[int] = Field(default=None, primary_key=True)
    namespace: str = Field(index=True, description="Job namespace (e.g., flowspec_examples)")
    name: str = Field(index=True, description="Job name (e.g., user_processing_etl)")
    
    # Enrichment fields
    system: Optional[str] = Field(default=None, description="System identifier")
    domain: Optional[str] = Field(default=None, description="Business domain")
    owner: Optional[str] = Field(default=None, description="Job owner")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})












