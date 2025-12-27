"""Business usage tracker for detecting and tracking business-facing jobs."""

from typing import Optional, List
from sqlmodel import Session, select
from flowspec.models import FSJob, FSDataset


class BusinessUsageTracker:
    """Service for detecting business-facing jobs and tracking dataset access."""

    # Business job name patterns
    BUSINESS_NAME_PATTERNS = [
        "_api",
        "_bi",
        "_dashboard",
        "_query",
        "_report",
        "_reporting"
    ]

    # Business system identifiers
    BUSINESS_SYSTEMS = [
        "api",
        "bi",
        "dashboard",
        "reporting"
    ]

    # Business-facing layers
    BUSINESS_LAYERS = [
        "bi",
        "app"
    ]

    def __init__(self, session: Session):
        """Initialize business usage tracker.
        
        Args:
            session: Database session
        """
        self.session = session

    def is_business_job(self, job: FSJob) -> bool:
        """Check if a job is business-facing based on job characteristics.
        
        Detection strategies:
        1. Job name contains business indicators (e.g., _api, _bi, _dashboard)
        2. Job system field is set to business system (e.g., api, bi, dashboard)
        3. Job outputs datasets with business layer (bi, app)
        
        Args:
            job: Job to check
            
        Returns:
            True if job is business-facing, False otherwise
        """
        # Strategy 1: Check job name patterns
        if self._has_business_name_pattern(job.name):
            return True

        # Strategy 2: Check job system field
        if job.system and job.system.lower() in self.BUSINESS_SYSTEMS:
            return True

        # Strategy 3: Check if job outputs datasets with business layer
        if self._outputs_business_layer(job):
            return True

        return False

    def _has_business_name_pattern(self, job_name: str) -> bool:
        """Check if job name contains business indicators.
        
        Args:
            job_name: Job name to check
            
        Returns:
            True if job name contains business pattern
        """
        job_name_lower = job_name.lower()
        return any(pattern in job_name_lower for pattern in self.BUSINESS_NAME_PATTERNS)

    def _outputs_business_layer(self, job: FSJob) -> bool:
        """Check if job outputs datasets with business layer (bi or app).
        
        Args:
            job: Job to check
            
        Returns:
            True if job outputs business layer datasets
        """
        from flowspec.models import FSEdge

        # Find all output edges for this job
        statement = select(FSEdge).where(
            FSEdge.job_id == job.id,
            FSEdge.edge_type == "output"
        )
        output_edges = self.session.exec(statement).all()

        # Check if any output dataset has business layer
        for edge in output_edges:
            dataset = self.session.get(FSDataset, edge.dataset_id)
            if dataset and dataset.layer and dataset.layer.lower() in self.BUSINESS_LAYERS:
                return True

        return False

    def get_input_datasets_for_job(self, job: FSJob) -> List[FSDataset]:
        """Get all input datasets for a job.
        
        Args:
            job: Job to get input datasets for
            
        Returns:
            List of input datasets
        """
        from flowspec.models import FSEdge

        # Find all input edges for this job
        statement = select(FSEdge).where(
            FSEdge.job_id == job.id,
            FSEdge.edge_type == "input"
        )
        input_edges = self.session.exec(statement).all()

        # Get datasets
        datasets = []
        for edge in input_edges:
            dataset = self.session.get(FSDataset, edge.dataset_id)
            if dataset:
                datasets.append(dataset)

        return datasets

    def update_dataset_access_metrics(
        self,
        dataset: FSDataset,
        access_time: Optional[float] = None
    ) -> None:
        """Update dataset access metrics (access_count and last_accessed_at).
        
        Args:
            dataset: Dataset to update
            access_time: Timestamp of access (defaults to current time)
        """
        from datetime import datetime

        # Increment access count
        dataset.access_count = (dataset.access_count or 0) + 1

        # Update last accessed time
        if access_time:
            dataset.last_accessed_at = datetime.fromtimestamp(access_time)
        else:
            dataset.last_accessed_at = datetime.utcnow()

        self.session.add(dataset)


