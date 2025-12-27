"""Complexity scoring service for calculating path complexity metrics."""

from typing import List, Dict, Optional, Tuple
from sqlmodel import Session, select
import networkx as nx
from flowspec.models import FSDataset, FSJob
from flowspec.path_analysis import PathFinder


class ComplexityScorer:
    """Service for calculating complexity metrics for data paths."""

    def __init__(self, session: Session, path_finder: Optional[PathFinder] = None):
        """Initialize complexity scorer.
        
        Args:
            session: Database session
            path_finder: PathFinder instance (creates new one if not provided)
        """
        self.session = session
        self.path_finder = path_finder or PathFinder(session)
        self._complexity_cache: Dict[Tuple[str, ...], Dict] = {}

    def calculate_path_complexity(self, path: List[str]) -> Dict:
        """Calculate complexity metrics for a single path.
        
        Args:
            path: List of node names representing a path (e.g., ["dataset1", "job1", "dataset2"])
            
        Returns:
            Dictionary with complexity metrics:
            - hop_count: Number of edges in the path
            - node_count: Number of nodes in the path
            - avg_fan_in: Average fan-in ratio for nodes in path
            - avg_fan_out: Average fan-out ratio for nodes in path
            - max_fan_in: Maximum fan-in for any node in path
            - max_fan_out: Maximum fan-out for any node in path
            - transform_density: Number of jobs per dataset in path
        """
        # Check cache
        path_tuple = tuple(path)
        if path_tuple in self._complexity_cache:
            return self._complexity_cache[path_tuple]

        graph = self.path_finder._build_graph()
        
        # Basic metrics
        hop_count = len(path) - 1  # Number of edges = nodes - 1
        node_count = len(path)
        
        # Calculate fan-in and fan-out for each node
        fan_ins = []
        fan_outs = []
        
        for node in path:
            if node in graph:
                fan_in = graph.in_degree(node)
                fan_out = graph.out_degree(node)
                fan_ins.append(fan_in)
                fan_outs.append(fan_out)
        
        # Calculate averages and maxes
        avg_fan_in = sum(fan_ins) / len(fan_ins) if fan_ins else 0.0
        avg_fan_out = sum(fan_outs) / len(fan_outs) if fan_outs else 0.0
        max_fan_in = max(fan_ins) if fan_ins else 0
        max_fan_out = max(fan_outs) if fan_outs else 0
        
        # Calculate transform density (jobs per dataset)
        # Count jobs in path
        job_count = 0
        dataset_count = 0
        
        for node in path:
            # Determine if node is a job or dataset by checking if it exists in database
            # Jobs are typically in namespace format, datasets are in namespace/name format
            # For now, we'll check if it's a job by trying to find it in jobs table
            parts = node.split("/")
            if len(parts) >= 2:
                namespace = "/".join(parts[:-1])
                name = parts[-1]
                
                # Check if it's a job
                job_stmt = select(FSJob).where(
                    FSJob.namespace == namespace,
                    FSJob.name == name
                )
                job = self.session.exec(job_stmt).first()
                
                if job:
                    job_count += 1
                else:
                    # Check if it's a dataset
                    dataset_stmt = select(FSDataset).where(
                        FSDataset.namespace == namespace,
                        FSDataset.name == name
                    )
                    dataset = self.session.exec(dataset_stmt).first()
                    if dataset:
                        dataset_count += 1
        
        transform_density = job_count / dataset_count if dataset_count > 0 else 0.0
        
        metrics = {
            "hop_count": hop_count,
            "node_count": node_count,
            "avg_fan_in": round(avg_fan_in, 2),
            "avg_fan_out": round(avg_fan_out, 2),
            "max_fan_in": max_fan_in,
            "max_fan_out": max_fan_out,
            "transform_density": round(transform_density, 2)
        }
        
        # Cache result
        self._complexity_cache[path_tuple] = metrics
        
        return metrics

    def calculate_paths_complexity(self, paths: List[List[str]]) -> List[Dict]:
        """Calculate complexity metrics for multiple paths.
        
        Args:
            paths: List of paths, where each path is a list of node names
            
        Returns:
            List of complexity metric dictionaries, one per path
        """
        return [self.calculate_path_complexity(path) for path in paths]

    def invalidate_cache(self):
        """Invalidate complexity cache (call after sync)."""
        self._complexity_cache.clear()












