"""FlowScope sync service for synchronizing data from Marquez."""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from flowspec.sync.marquez_client import MarquezClient
from flowspec.models import FSDataset, FSJob, FSEdge, FSRun
from flowspec.business_usage import BusinessUsageTracker


class SyncService:
    """Service for synchronizing lineage data from Marquez to FlowScope."""

    def __init__(self, session: Session, marquez_client: Optional[MarquezClient] = None):
        """Initialize sync service.
        
        Args:
            session: Database session
            marquez_client: Marquez API client (creates new one if not provided)
        """
        self.session = session
        self.marquez_client = marquez_client or MarquezClient()
        self.usage_tracker = BusinessUsageTracker(session)

    async def sync_all(self, last_sync_time: Optional[datetime] = None) -> dict:
        """Sync all lineage data from Marquez.
        
        Args:
            last_sync_time: Only sync data updated after this time (for incremental sync)
            
        Returns:
            Dictionary with sync statistics
        """
        stats = {
            "namespaces": 0,
            "jobs": 0,
            "datasets": 0,
            "runs": 0,
            "edges": 0,
            "business_usage_updates": 0,
            "errors": []
        }

        try:
            # Get all namespaces
            namespaces = await self.marquez_client.get_namespaces()
            stats["namespaces"] = len(namespaces)

            # Sync each namespace
            for namespace in namespaces:
                try:
                    await self._sync_namespace(namespace, last_sync_time, stats)
                except Exception as e:
                    error_msg = f"Error syncing namespace {namespace}: {str(e)}"
                    stats["errors"].append(error_msg)
                    print(f"⚠️  {error_msg}")

            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Sync failed: {str(e)}")

        return stats

    async def _sync_namespace(
        self, namespace: str, last_sync_time: Optional[datetime], stats: dict
    ):
        """Sync all data for a namespace."""
        # Sync jobs
        jobs_data = await self.marquez_client.get_jobs(namespace, limit=1000)
        for job_data in jobs_data.get("jobs", []):
            await self._sync_job(namespace, job_data, stats)

        # Sync datasets
        datasets_data = await self.marquez_client.get_datasets(namespace, limit=1000)
        for dataset_data in datasets_data.get("datasets", []):
            await self._sync_dataset(namespace, dataset_data, stats)

        # Sync runs and edges for each job
        for job_data in jobs_data.get("jobs", []):
            job_name = job_data.get("name")
            if job_name:
                await self._sync_job_runs_and_edges(namespace, job_name, stats)

    async def _sync_job(self, namespace: str, job_data: dict, stats: dict):
        """Sync a single job."""
        job_name = job_data.get("name")
        if not job_name:
            return

        # Check if job exists
        statement = select(FSJob).where(
            FSJob.namespace == namespace,
            FSJob.name == job_name
        )
        existing_job = self.session.exec(statement).first()

        if existing_job:
            # Update existing job
            existing_job.updated_at = datetime.utcnow()
            job = existing_job
        else:
            # Create new job
            job = FSJob(
                namespace=namespace,
                name=job_name,
                system=job_data.get("type"),  # Use job type as system hint
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(job)
            stats["jobs"] += 1

        self.session.add(job)

    async def _sync_dataset(self, namespace: str, dataset_data: dict, stats: dict):
        """Sync a single dataset."""
        dataset_name = dataset_data.get("name")
        if not dataset_name:
            return

        # Check if dataset exists
        statement = select(FSDataset).where(
            FSDataset.namespace == namespace,
            FSDataset.name == dataset_name
        )
        existing_dataset = self.session.exec(statement).first()

        if existing_dataset:
            # Update existing dataset
            existing_dataset.updated_at = datetime.utcnow()
            dataset = existing_dataset
        else:
            # Create new dataset
            dataset = FSDataset(
                namespace=namespace,
                name=dataset_name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(dataset)
            stats["datasets"] += 1

        self.session.add(dataset)

    async def _sync_job_runs_and_edges(
        self, namespace: str, job_name: str, stats: dict
    ):
        """Sync runs and edges for a job."""
        # Get job lineage (includes inputs and outputs)
        try:
            lineage_data = await self.marquez_client.get_job_lineage(namespace, job_name)
        except Exception as e:
            print(f"⚠️  Could not fetch lineage for {namespace}/{job_name}: {str(e)}")
            return

        # Get job from database
        statement = select(FSJob).where(
            FSJob.namespace == namespace,
            FSJob.name == job_name
        )
        job = self.session.exec(statement).first()
        if not job:
            return

        # Sync inputs (edges)
        inputs = lineage_data.get("inputs", [])
        for input_data in inputs:
            await self._sync_edge(job.id, input_data, "input", namespace, stats)

        # Sync outputs (edges)
        outputs = lineage_data.get("outputs", [])
        for output_data in outputs:
            await self._sync_edge(job.id, output_data, "output", namespace, stats)

        # Sync runs
        try:
            runs_data = await self.marquez_client.get_job_runs(namespace, job_name, limit=100)
            for run_data in runs_data.get("runs", []):
                await self._sync_run(job.id, run_data, stats)
        except Exception as e:
            print(f"⚠️  Could not fetch runs for {namespace}/{job_name}: {str(e)}")

    async def _sync_edge(
        self, job_id: int, dataset_data: dict, edge_type: str, namespace: str, stats: dict
    ):
        """Sync an edge (input or output relationship)."""
        dataset_namespace = dataset_data.get("namespace", namespace)
        dataset_name = dataset_data.get("name")
        if not dataset_name:
            return

        # Get or create dataset
        statement = select(FSDataset).where(
            FSDataset.namespace == dataset_namespace,
            FSDataset.name == dataset_name
        )
        dataset = self.session.exec(statement).first()

        if not dataset:
            # Create dataset if it doesn't exist
            dataset = FSDataset(
                namespace=dataset_namespace,
                name=dataset_name,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.session.add(dataset)
            self.session.flush()  # Flush to get dataset.id
            stats["datasets"] += 1

        # Check if edge exists
        statement = select(FSEdge).where(
            FSEdge.job_id == job_id,
            FSEdge.dataset_id == dataset.id,
            FSEdge.edge_type == edge_type
        )
        existing_edge = self.session.exec(statement).first()

        if not existing_edge:
            # Create new edge
            edge = FSEdge(
                job_id=job_id,
                dataset_id=dataset.id,
                edge_type=edge_type,
                created_at=datetime.utcnow()
            )
            self.session.add(edge)
            stats["edges"] += 1

    async def _sync_run(self, job_id: int, run_data: dict, stats: dict):
        """Sync a run and update business usage metrics if applicable."""
        run_id = run_data.get("id")
        if not run_id:
            return

        # Get job
        job = self.session.get(FSJob, job_id)
        if not job:
            return

        # Check if run exists
        statement = select(FSRun).where(FSRun.run_id == run_id)
        existing_run = self.session.exec(statement).first()

        run_state = run_data.get("state", "complete")
        completed_at = self._parse_timestamp(run_data.get("endedAt"))

        if existing_run:
            # Update existing run
            existing_run.state = run_state
            existing_run.started_at = self._parse_timestamp(run_data.get("startedAt"))
            existing_run.completed_at = completed_at
            run = existing_run
        else:
            # Create new run
            run = FSRun(
                job_id=job_id,
                run_id=run_id,
                state=run_state,
                started_at=self._parse_timestamp(run_data.get("startedAt")),
                completed_at=completed_at,
                created_at=datetime.utcnow()
            )
            self.session.add(run)
            stats["runs"] += 1

        # Update business usage metrics if job is business-facing and run completed
        if run_state == "complete" and self.usage_tracker.is_business_job(job):
            input_datasets = self.usage_tracker.get_input_datasets_for_job(job)
            for dataset in input_datasets:
                # Use run completion time for access timestamp
                access_timestamp = None
                if completed_at:
                    access_timestamp = completed_at.timestamp()
                
                self.usage_tracker.update_dataset_access_metrics(
                    dataset,
                    access_time=access_timestamp
                )
                stats["business_usage_updates"] += 1

    def _parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """Parse timestamp string to datetime."""
        if not timestamp_str:
            return None
        try:
            # Marquez returns ISO format timestamps
            return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        except Exception:
            return None




