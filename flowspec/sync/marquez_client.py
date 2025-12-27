"""Marquez API client for fetching lineage data."""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import httpx


class MarquezClient:
    """Client for interacting with Marquez API."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize Marquez client.
        
        Args:
            base_url: Marquez API base URL (defaults to MARQUEZ_URL env var or http://localhost:5002)
        """
        self.base_url = base_url or os.getenv("MARQUEZ_URL", "http://localhost:5002")
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def get_namespaces(self) -> List[str]:
        """Get list of all namespaces."""
        response = await self.client.get("/api/v1/namespaces")
        response.raise_for_status()
        data = response.json()
        return [ns["name"] for ns in data.get("namespaces", [])]

    async def get_jobs(self, namespace: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get jobs for a namespace.
        
        Args:
            namespace: Namespace name
            limit: Maximum number of jobs to return
            offset: Offset for pagination
            
        Returns:
            Dictionary with 'jobs' list and 'totalCount'
        """
        response = await self.client.get(
            f"/api/v1/namespaces/{namespace}/jobs",
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()

    async def get_datasets(self, namespace: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get datasets for a namespace.
        
        Args:
            namespace: Namespace name
            limit: Maximum number of datasets to return
            offset: Offset for pagination
            
        Returns:
            Dictionary with 'datasets' list and 'totalCount'
        """
        response = await self.client.get(
            f"/api/v1/namespaces/{namespace}/datasets",
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()

    async def get_job_runs(
        self, namespace: str, job_name: str, limit: int = 100, offset: int = 0
    ) -> Dict[str, Any]:
        """Get runs for a job.
        
        Args:
            namespace: Namespace name
            job_name: Job name
            limit: Maximum number of runs to return
            offset: Offset for pagination
            
        Returns:
            Dictionary with 'runs' list
        """
        response = await self.client.get(
            f"/api/v1/namespaces/{namespace}/jobs/{job_name}/runs",
            params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()
        return response.json()

    async def get_job_lineage(
        self, namespace: str, job_name: str, depth: int = 20
    ) -> Dict[str, Any]:
        """Get lineage for a job (includes inputs and outputs).
        
        Args:
            namespace: Namespace name
            job_name: Job name
            depth: Lineage depth
            
        Returns:
            Dictionary with job lineage including inputs and outputs
        """
        response = await self.client.get(
            f"/api/v1/namespaces/{namespace}/jobs/{job_name}",
            params={"depth": depth}
        )
        response.raise_for_status()
        return response.json()

    async def get_dataset_lineage(
        self, namespace: str, dataset_name: str, depth: int = 20
    ) -> Dict[str, Any]:
        """Get lineage for a dataset (includes upstream and downstream).
        
        Args:
            namespace: Namespace name
            dataset_name: Dataset name
            depth: Lineage depth
            
        Returns:
            Dictionary with dataset lineage including upstream and downstream
        """
        response = await self.client.get(
            f"/api/v1/namespaces/{namespace}/datasets/{dataset_name}",
            params={"depth": depth}
        )
        response.raise_for_status()
        return response.json()












