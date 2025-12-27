"""Dataset model for FlowScope."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class FSDataset(SQLModel, table=True):
    """Dataset model representing a data artifact (table, file, API response)."""

    __tablename__ = "fs_dataset"

    id: Optional[int] = Field(default=None, primary_key=True)
    namespace: str = Field(index=True, description="Dataset namespace (e.g., postgresql://localhost:5432)")
    name: str = Field(index=True, description="Dataset name (e.g., raw.users)")
    
    # Enrichment fields
    layer: Optional[str] = Field(
        default=None,
        index=True,
        description="Data layer: raw, ods, dwd, dws, app, bi"
    )
    system: Optional[str] = Field(default=None, description="System identifier")
    domain: Optional[str] = Field(default=None, description="Business domain")
    owner: Optional[str] = Field(default=None, description="Dataset owner")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    
    # Activity metrics (for future use)
    last_accessed_at: Optional[datetime] = Field(default=None, description="Last time dataset was accessed")
    access_count: int = Field(default=0, description="Number of times dataset was accessed")












