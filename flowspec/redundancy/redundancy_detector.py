"""Redundancy detection service for identifying orphan datasets and duplicate tables."""

from typing import List, Dict, Optional, Set, Tuple
from sqlmodel import Session, select
from difflib import SequenceMatcher
import networkx as nx
from flowspec.models import FSDataset, FSEdge
from flowspec.path_analysis import PathFinder


class RedundancyDetector:
    """Service for detecting redundant datasets (orphans and duplicates)."""

    def __init__(self, session: Session, path_finder: Optional[PathFinder] = None):
        """Initialize redundancy detector.
        
        Args:
            session: Database session
            path_finder: PathFinder instance (creates new one if not provided)
        """
        self.session = session
        self.path_finder = path_finder or PathFinder(session)

    def find_orphan_datasets(self) -> List[Dict]:
        """Find orphan datasets (no upstream AND no downstream connections).
        
        Returns:
            List of orphan dataset dictionaries with metadata
        """
        graph = self.path_finder._build_graph()
        
        # Get all datasets
        datasets = self.session.exec(select(FSDataset)).all()
        
        orphans = []
        for dataset in datasets:
            node = f"{dataset.namespace}/{dataset.name}"
            
            # Check if node has any connections
            has_upstream = graph.in_degree(node) > 0
            has_downstream = graph.out_degree(node) > 0
            
            # Orphan: no upstream AND no downstream
            if not has_upstream and not has_downstream:
                orphans.append({
                    "id": dataset.id,
                    "namespace": dataset.namespace,
                    "name": dataset.name,
                    "layer": dataset.layer,
                    "system": dataset.system,
                    "domain": dataset.domain,
                    "owner": dataset.owner,
                    "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
                    "status": "orphan",
                    "recommendation": "candidate_for_deletion"
                })
        
        return orphans

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names using SequenceMatcher.
        
        Args:
            name1: First name
            name2: Second name
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        return SequenceMatcher(None, name1.lower(), name2.lower()).ratio()

    def _get_paths_for_dataset(self, dataset: FSDataset) -> Tuple[Set[str], Set[str]]:
        """Get upstream and downstream paths for a dataset.
        
        Args:
            dataset: Dataset to get paths for
            
        Returns:
            Tuple of (upstream_path_nodes, downstream_path_nodes) as sets
        """
        graph = self.path_finder._build_graph()
        node = f"{dataset.namespace}/{dataset.name}"
        
        if node not in graph:
            return set(), set()
        
        # Get all upstream nodes (ancestors)
        upstream_nodes = set()
        try:
            for ancestor in nx.ancestors(graph, node):
                upstream_nodes.add(ancestor)
        except nx.NetworkXError:
            pass
        
        # Get all downstream nodes (descendants)
        downstream_nodes = set()
        try:
            for descendant in nx.descendants(graph, node):
                downstream_nodes.add(descendant)
        except nx.NetworkXError:
            pass
        
        return upstream_nodes, downstream_nodes

    def _calculate_path_overlap(
        self, 
        paths1: Tuple[Set[str], Set[str]], 
        paths2: Tuple[Set[str], Set[str]]
    ) -> float:
        """Calculate path overlap between two datasets.
        
        Args:
            paths1: (upstream_nodes, downstream_nodes) for first dataset
            paths2: (upstream_nodes, downstream_nodes) for second dataset
            
        Returns:
            Overlap score between 0.0 and 1.0
        """
        upstream1, downstream1 = paths1
        upstream2, downstream2 = paths2
        
        # Calculate Jaccard similarity for upstream and downstream
        upstream_intersection = len(upstream1 & upstream2)
        upstream_union = len(upstream1 | upstream2)
        upstream_overlap = upstream_intersection / upstream_union if upstream_union > 0 else 0.0
        
        downstream_intersection = len(downstream1 & downstream2)
        downstream_union = len(downstream1 | downstream2)
        downstream_overlap = downstream_intersection / downstream_union if downstream_union > 0 else 0.0
        
        # Average of upstream and downstream overlap
        return (upstream_overlap + downstream_overlap) / 2.0

    def find_duplicate_candidates(
        self, 
        similarity_threshold: float = 0.7,
        path_overlap_threshold: float = 0.5
    ) -> List[Dict]:
        """Find duplicate table candidates based on name similarity, layer matching, and path overlap.
        
        Args:
            similarity_threshold: Minimum name similarity score (0.0-1.0)
            path_overlap_threshold: Minimum path overlap score (0.0-1.0)
            
        Returns:
            List of duplicate candidate groups
        """
        # Get all datasets
        datasets = self.session.exec(select(FSDataset)).all()
        
        # Group by layer for efficiency
        datasets_by_layer: Dict[str, List[FSDataset]] = {}
        for dataset in datasets:
            layer = dataset.layer or "unknown"
            if layer not in datasets_by_layer:
                datasets_by_layer[layer] = []
            datasets_by_layer[layer].append(dataset)
        
        # Find duplicates within each layer
        duplicate_groups = []
        processed = set()
        
        for layer, layer_datasets in datasets_by_layer.items():
            for i, dataset1 in enumerate(layer_datasets):
                if dataset1.id in processed:
                    continue
                
                group = [dataset1]
                paths1 = self._get_paths_for_dataset(dataset1)
                
                for dataset2 in layer_datasets[i + 1:]:
                    if dataset2.id in processed:
                        continue
                    
                    # Check name similarity
                    name_similarity = self._calculate_name_similarity(
                        dataset1.name, dataset2.name
                    )
                    
                    if name_similarity >= similarity_threshold:
                        # Check path overlap
                        paths2 = self._get_paths_for_dataset(dataset2)
                        path_overlap = self._calculate_path_overlap(paths1, paths2)
                        
                        if path_overlap >= path_overlap_threshold:
                            group.append(dataset2)
                            processed.add(dataset2.id)
                
                if len(group) > 1:
                    processed.add(dataset1.id)
                    # Calculate average similarity for the group
                    avg_similarity = sum(
                        self._calculate_name_similarity(group[0].name, d.name)
                        for d in group[1:]
                    ) / len(group[1:]) if len(group) > 1 else 0.0
                    
                    duplicate_groups.append({
                        "group_id": len(duplicate_groups),
                        "count": len(group),
                        "average_similarity": round(avg_similarity, 3),
                        "layer": layer,
                        "candidates": [
                            {
                                "id": d.id,
                                "namespace": d.namespace,
                                "name": d.name,
                                "system": d.system,
                                "domain": d.domain,
                                "owner": d.owner,
                                "created_at": d.created_at.isoformat() if d.created_at else None,
                            }
                            for d in group
                        ],
                        "status": "duplicate_candidate",
                        "recommendation": "candidate_for_merging"
                    })
        
        return duplicate_groups












