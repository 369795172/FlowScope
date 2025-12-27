"""Path analysis engine for finding upstream and downstream paths."""

from typing import List, Optional, Set, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
import networkx as nx
from flowspec.models import FSDataset, FSJob, FSEdge


class PathFinder:
    """Service for finding paths in the lineage graph."""

    def __init__(self, session: Session):
        """Initialize path finder.
        
        Args:
            session: Database session
        """
        self.session = session
        self._graph_cache: Optional[nx.DiGraph] = None

    def _build_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from database."""
        if self._graph_cache is not None:
            return self._graph_cache

        graph = nx.DiGraph()

        # Get all edges
        statement = select(FSEdge)
        edges = self.session.exec(statement).all()

        # Get all datasets and jobs for node metadata
        datasets = {d.id: d for d in self.session.exec(select(FSDataset)).all()}
        jobs = {j.id: j for j in self.session.exec(select(FSJob)).all()}

        # Add edges to graph
        for edge in edges:
            dataset = datasets.get(edge.dataset_id)
            job = jobs.get(edge.job_id)

            if not dataset or not job:
                continue

            dataset_node = f"{dataset.namespace}/{dataset.name}"
            job_node = f"{job.namespace}/{job.name}"

            if edge.edge_type == "input":
                # Dataset -> Job
                graph.add_edge(dataset_node, job_node, edge_id=edge.id)
            elif edge.edge_type == "output":
                # Job -> Dataset
                graph.add_edge(job_node, dataset_node, edge_id=edge.id)

        self._graph_cache = graph
        return graph

    def invalidate_cache(self):
        """Invalidate graph cache (call after sync)."""
        self._graph_cache = None

    def find_upstream_paths(
        self,
        namespace: str,
        dataset_name: str,
        max_depth: int = 20,
        from_layer: Optional[str] = None,
        include_business_usage: bool = False,
        filter_business_only: bool = False
    ) -> List[List[str]]:
        """Find all upstream paths (sources) leading to a dataset.
        
        Args:
            namespace: Dataset namespace
            dataset_name: Dataset name
            max_depth: Maximum path depth
            from_layer: Filter paths to start from this layer (e.g., "raw")
            include_business_usage: Whether to include business usage indicators
            filter_business_only: If True, only return paths with business usage
            
        Returns:
            List of paths, where each path is a list of node names
        """
        graph = self._build_graph()
        target = f"{namespace}/{dataset_name}"

        if target not in graph:
            return []

        # Find all source nodes (nodes with no incoming edges)
        sources = [n for n in graph.nodes() if graph.in_degree(n) == 0]

        # Filter sources by layer if specified
        if from_layer:
            sources = self._filter_by_layer(sources, from_layer)

        # Find all simple paths from sources to target
        all_paths = []
        for source in sources:
            try:
                paths = list(nx.all_simple_paths(
                    graph, source, target, cutoff=max_depth
                ))
                all_paths.extend(paths)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

        # Filter by business usage if requested
        if filter_business_only:
            all_paths = [p for p in all_paths if self._path_has_business_usage(p)]

        return all_paths

    def find_downstream_paths(
        self,
        namespace: str,
        dataset_name: str,
        max_depth: int = 20,
        to_layer: Optional[str] = None,
        include_business_usage: bool = False,
        filter_business_only: bool = False
    ) -> List[List[str]]:
        """Find all downstream paths (destinations) from a dataset.
        
        Args:
            namespace: Dataset namespace
            dataset_name: Dataset name
            max_depth: Maximum path depth
            to_layer: Filter paths to end at this layer (e.g., "bi")
            include_business_usage: Whether to include business usage indicators
            filter_business_only: If True, only return paths with business usage
            
        Returns:
            List of paths, where each path is a list of node names
        """
        graph = self._build_graph()
        source = f"{namespace}/{dataset_name}"

        if source not in graph:
            return []

        # Find all sink nodes (nodes with no outgoing edges)
        sinks = [n for n in graph.nodes() if graph.out_degree(n) == 0]

        # Filter sinks by layer if specified
        if to_layer:
            sinks = self._filter_by_layer(sinks, to_layer)

        # Find all simple paths from source to sinks
        all_paths = []
        for sink in sinks:
            try:
                paths = list(nx.all_simple_paths(
                    graph, source, sink, cutoff=max_depth
                ))
                all_paths.extend(paths)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

        # Filter by business usage if requested
        if filter_business_only:
            all_paths = [p for p in all_paths if self._path_has_business_usage(p)]

        return all_paths

    def find_filtered_paths(
        self,
        namespace: str,
        dataset_name: str,
        from_layer: Optional[str] = None,
        to_layer: Optional[str] = None,
        max_depth: int = 20,
        include_business_usage: bool = False,
        filter_business_only: bool = False
    ) -> List[List[str]]:
        """Find paths with layer filtering (e.g., raw → bi).
        
        Args:
            namespace: Dataset namespace
            dataset_name: Dataset name
            from_layer: Filter paths to start from this layer
            to_layer: Filter paths to end at this layer
            max_depth: Maximum path depth
            include_business_usage: Whether to include business usage indicators
            filter_business_only: If True, only return paths with business usage
            
        Returns:
            List of paths
        """
        if from_layer and to_layer:
            # Find paths from source layer to target layer
            # Start from target dataset and find upstream paths from source layer
            upstream_paths = self.find_upstream_paths(
                namespace, dataset_name, max_depth, from_layer,
                include_business_usage=include_business_usage,
                filter_business_only=filter_business_only
            )
            # Filter to only include paths ending at target dataset (which should be in to_layer)
            # Actually, we want paths that start at from_layer and end at to_layer
            # Since we're querying from the target dataset, we need to check if target is in to_layer
            target_node = f"{namespace}/{dataset_name}"
            if self._node_in_layer(target_node, to_layer):
                return upstream_paths
            else:
                return []
        elif from_layer:
            return self.find_upstream_paths(
                namespace, dataset_name, max_depth, from_layer,
                include_business_usage=include_business_usage,
                filter_business_only=filter_business_only
            )
        elif to_layer:
            return self.find_downstream_paths(
                namespace, dataset_name, max_depth, to_layer,
                include_business_usage=include_business_usage,
                filter_business_only=filter_business_only
            )
        else:
            # No filtering, return both upstream and downstream
            upstream = self.find_upstream_paths(
                namespace, dataset_name, max_depth,
                include_business_usage=include_business_usage,
                filter_business_only=filter_business_only
            )
            downstream = self.find_downstream_paths(
                namespace, dataset_name, max_depth,
                include_business_usage=include_business_usage,
                filter_business_only=filter_business_only
            )
            return upstream + downstream

    def _filter_by_layer(self, nodes: List[str], layer: str) -> List[str]:
        """Filter nodes by layer."""
        filtered = []
        for node in nodes:
            if self._node_in_layer(node, layer):
                filtered.append(node)
        return filtered

    def _node_in_layer(self, node: Optional[str], layer: str) -> bool:
        """Check if a node (dataset) is in the specified layer."""
        if not node:
            return False

        # Extract namespace and name from node (format: namespace/name)
        parts = node.split("/")
        if len(parts) < 2:
            return False

        namespace = "/".join(parts[:-1])
        dataset_name = parts[-1]

        # Query dataset from database
        statement = select(FSDataset).where(
            FSDataset.namespace == namespace,
            FSDataset.name == dataset_name
        )
        dataset = self.session.exec(statement).first()

        return dataset and dataset.layer == layer

    def _path_has_business_usage(self, path: List[str]) -> bool:
        """Check if a path includes datasets with business usage.
        
        Args:
            path: List of node names (datasets and jobs)
            
        Returns:
            True if path includes datasets with business usage
        """
        for node in path:
            # Only check datasets (not jobs)
            if self._is_dataset_node(node):
                if self._dataset_has_business_usage(node):
                    return True
        return False

    def _is_dataset_node(self, node: str) -> bool:
        """Check if a node is a dataset (not a job).
        
        Note: This is a heuristic - we check if the node exists as a dataset.
        In the graph, both datasets and jobs are nodes, but we can distinguish
        by checking if it exists in the dataset table.
        """
        parts = node.split("/")
        if len(parts) < 2:
            return False

        namespace = "/".join(parts[:-1])
        dataset_name = parts[-1]

        statement = select(FSDataset).where(
            FSDataset.namespace == namespace,
            FSDataset.name == dataset_name
        )
        dataset = self.session.exec(statement).first()
        return dataset is not None

    def _dataset_has_business_usage(self, node: str) -> bool:
        """Check if a dataset has business usage (access_count > 0).
        
        Args:
            node: Node name (format: namespace/name)
            
        Returns:
            True if dataset has business usage
        """
        parts = node.split("/")
        if len(parts) < 2:
            return False

        namespace = "/".join(parts[:-1])
        dataset_name = parts[-1]

        statement = select(FSDataset).where(
            FSDataset.namespace == namespace,
            FSDataset.name == dataset_name
        )
        dataset = self.session.exec(statement).first()

        if not dataset:
            return False

        return (dataset.access_count or 0) > 0

    def get_path_business_usage_indicators(self, path: List[str]) -> Dict[str, Any]:
        """Get business usage indicators for each node in a path.
        
        Args:
            path: List of node names
            
        Returns:
            Dictionary mapping node names to business usage info
        """
        indicators = {}
        for node in path:
            if self._is_dataset_node(node):
                indicators[node] = {
                    "has_business_usage": self._dataset_has_business_usage(node),
                    "access_count": self._get_dataset_access_count(node),
                    "last_accessed_at": self._get_dataset_last_accessed(node)
                }
            else:
                indicators[node] = {
                    "has_business_usage": False,
                    "node_type": "job"
                }
        return indicators

    def _get_dataset_access_count(self, node: str) -> int:
        """Get access count for a dataset node."""
        parts = node.split("/")
        if len(parts) < 2:
            return 0

        namespace = "/".join(parts[:-1])
        dataset_name = parts[-1]

        statement = select(FSDataset).where(
            FSDataset.namespace == namespace,
            FSDataset.name == dataset_name
        )
        dataset = self.session.exec(statement).first()

        return (dataset.access_count or 0) if dataset else 0

    def _get_dataset_last_accessed(self, node: str) -> Optional[datetime]:
        """Get last accessed timestamp for a dataset node."""
        parts = node.split("/")
        if len(parts) < 2:
            return None

        namespace = "/".join(parts[:-1])
        dataset_name = parts[-1]

        statement = select(FSDataset).where(
            FSDataset.namespace == namespace,
            FSDataset.name == dataset_name
        )
        dataset = self.session.exec(statement).first()

        return dataset.last_accessed_at if dataset else None

