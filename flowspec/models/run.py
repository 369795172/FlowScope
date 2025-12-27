"""Run model for FlowScope representing job execution instances."""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Column, String


class FSRun(SQLModel, table=True):
    """Run model representing a single execution instance of a Job."""

    __tablename__ = "fs_run"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="fs_job.id", index=True, description="Reference to job")
    run_id: str = Field(index=True, unique=True, description="Run ID from Marquez (UUID)")
    state: str = Field(sa_column=Column(String), description="Run state: start, complete, abort, or fail")
    
    # Timestamps
    started_at: Optional[datetime] = Field(default=None, description="When run started")
    completed_at: Optional[datetime] = Field(default=None, description="When run completed")
    created_at: datetime = Field(default_factory=datetime.utcnow)

