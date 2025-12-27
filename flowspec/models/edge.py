"""Edge model for FlowScope representing relationships between Jobs and Datasets."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, String


class FSEdge(SQLModel, table=True):
    """Edge model representing input/output relationships between Jobs and Datasets."""

    __tablename__ = "fs_edge"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="fs_job.id", index=True, description="Reference to job")
    dataset_id: int = Field(foreign_key="fs_dataset.id", index=True, description="Reference to dataset")
    edge_type: str = Field(sa_column=Column(String), description="Type of edge: input or output")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

