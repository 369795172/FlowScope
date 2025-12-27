"""FastAPI application for FlowScope."""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from flowspec.db.config import get_session
from flowspec.path_analysis import PathFinder
from flowspec.complexity import ComplexityScorer
from flowspec.redundancy import RedundancyDetector
from flowspec.models import FSDataset

app = FastAPI(
    title="FlowScope API",
    description="Data lineage analysis and path query API",
    version="0.1.0"
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1/datasets/{namespace}/{name}/upstream")
async def get_upstream_paths(
    namespace: str,
    name: str,
    max_depth: int = Query(default=20, ge=1, le=50),
    from_layer: Optional[str] = Query(default=None, description="Filter by source layer (e.g., raw)"),
    include_complexity: bool = Query(default=True, description="Include complexity metrics in response"),
    include_business_usage: bool = Query(default=True, description="Include business usage indicators"),
    filter_business_only: bool = Query(default=False, description="Only return paths with business usage"),
    session: Session = Depends(get_session)
):
    """Get all upstream paths (sources) leading to a dataset.
    
    Args:
        namespace: Dataset namespace
        name: Dataset name
        max_depth: Maximum path depth
        from_layer: Filter paths to start from this layer
        include_complexity: Whether to include complexity metrics
        include_business_usage: Whether to include business usage indicators
        filter_business_only: Only return paths with business usage
        
    Returns:
        List of paths with optional complexity metrics and business usage indicators
    """
    path_finder = PathFinder(session)
    paths = path_finder.find_upstream_paths(
        namespace, name, max_depth=max_depth, from_layer=from_layer,
        include_business_usage=include_business_usage,
        filter_business_only=filter_business_only
    )
    
    result: Dict[str, Any] = {"paths": paths, "count": len(paths)}
    
    if include_complexity and paths:
        complexity_scorer = ComplexityScorer(session, path_finder)
        complexity_metrics = complexity_scorer.calculate_paths_complexity(paths)
        result["complexity"] = complexity_metrics
        # Also include complexity with each path
        result["paths_with_complexity"] = [
            {"path": path, "complexity": metrics}
            for path, metrics in zip(paths, complexity_metrics)
        ]
    
    if include_business_usage and paths:
        business_usage_indicators = [
            path_finder.get_path_business_usage_indicators(path) for path in paths
        ]
        result["business_usage"] = business_usage_indicators
        result["paths_with_business_usage"] = [
            {
                "path": path,
                "business_usage": indicators,
                "is_business_critical": any(
                    info.get("has_business_usage", False) for info in indicators.values()
                )
            }
            for path, indicators in zip(paths, business_usage_indicators)
        ]
    
    return result


@app.get("/api/v1/datasets/{namespace}/{name}/downstream")
async def get_downstream_paths(
    namespace: str,
    name: str,
    max_depth: int = Query(default=20, ge=1, le=50),
    to_layer: Optional[str] = Query(default=None, description="Filter by destination layer (e.g., bi)"),
    include_complexity: bool = Query(default=True, description="Include complexity metrics in response"),
    include_business_usage: bool = Query(default=True, description="Include business usage indicators"),
    filter_business_only: bool = Query(default=False, description="Only return paths with business usage"),
    session: Session = Depends(get_session)
):
    """Get all downstream paths (destinations) from a dataset.
    
    Args:
        namespace: Dataset namespace
        name: Dataset name
        max_depth: Maximum path depth
        to_layer: Filter paths to end at this layer
        include_complexity: Whether to include complexity metrics
        include_business_usage: Whether to include business usage indicators
        filter_business_only: Only return paths with business usage
        
    Returns:
        List of paths with optional complexity metrics and business usage indicators
    """
    path_finder = PathFinder(session)
    paths = path_finder.find_downstream_paths(
        namespace, name, max_depth=max_depth, to_layer=to_layer,
        include_business_usage=include_business_usage,
        filter_business_only=filter_business_only
    )
    
    result: Dict[str, Any] = {"paths": paths, "count": len(paths)}
    
    if include_complexity and paths:
        complexity_scorer = ComplexityScorer(session, path_finder)
        complexity_metrics = complexity_scorer.calculate_paths_complexity(paths)
        result["complexity"] = complexity_metrics
        # Also include complexity with each path
        result["paths_with_complexity"] = [
            {"path": path, "complexity": metrics}
            for path, metrics in zip(paths, complexity_metrics)
        ]
    
    if include_business_usage and paths:
        business_usage_indicators = [
            path_finder.get_path_business_usage_indicators(path) for path in paths
        ]
        result["business_usage"] = business_usage_indicators
        result["paths_with_business_usage"] = [
            {
                "path": path,
                "business_usage": indicators,
                "is_business_critical": any(
                    info.get("has_business_usage", False) for info in indicators.values()
                )
            }
            for path, indicators in zip(paths, business_usage_indicators)
        ]
    
    return result


@app.get("/api/v1/datasets/{namespace}/{name}/paths")
async def get_filtered_paths(
    namespace: str,
    name: str,
    from_layer: Optional[str] = Query(default=None, description="Filter by source layer (e.g., raw)"),
    to_layer: Optional[str] = Query(default=None, description="Filter by destination layer (e.g., bi)"),
    max_depth: int = Query(default=20, ge=1, le=50),
    include_complexity: bool = Query(default=True, description="Include complexity metrics in response"),
    include_business_usage: bool = Query(default=True, description="Include business usage indicators"),
    filter_business_only: bool = Query(default=False, description="Only return paths with business usage"),
    session: Session = Depends(get_session)
):
    """Get filtered paths (e.g., raw → bi).
    
    Args:
        namespace: Dataset namespace
        name: Dataset name
        from_layer: Filter paths to start from this layer
        to_layer: Filter paths to end at this layer
        max_depth: Maximum path depth
        include_complexity: Whether to include complexity metrics
        include_business_usage: Whether to include business usage indicators
        filter_business_only: Only return paths with business usage
        
    Returns:
        List of paths with optional complexity metrics and business usage indicators
    """
    path_finder = PathFinder(session)
    paths = path_finder.find_filtered_paths(
        namespace, name,
        from_layer=from_layer,
        to_layer=to_layer,
        max_depth=max_depth,
        include_business_usage=include_business_usage,
        filter_business_only=filter_business_only
    )
    
    result: Dict[str, Any] = {"paths": paths, "count": len(paths)}
    
    if include_complexity and paths:
        complexity_scorer = ComplexityScorer(session, path_finder)
        complexity_metrics = complexity_scorer.calculate_paths_complexity(paths)
        result["complexity"] = complexity_metrics
        # Also include complexity with each path
        result["paths_with_complexity"] = [
            {"path": path, "complexity": metrics}
            for path, metrics in zip(paths, complexity_metrics)
        ]
    
    if include_business_usage and paths:
        business_usage_indicators = [
            path_finder.get_path_business_usage_indicators(path) for path in paths
        ]
        result["business_usage"] = business_usage_indicators
        result["paths_with_business_usage"] = [
            {
                "path": path,
                "business_usage": indicators,
                "is_business_critical": any(
                    info.get("has_business_usage", False) for info in indicators.values()
                )
            }
            for path, indicators in zip(paths, business_usage_indicators)
        ]
    
    return result


@app.get("/api/v1/datasets/{namespace}/{name}/complexity")
async def get_dataset_complexity(
    namespace: str,
    name: str,
    max_depth: int = Query(default=20, ge=1, le=50),
    session: Session = Depends(get_session)
):
    """Get complexity metrics for all paths involving a dataset.
    
    Args:
        namespace: Dataset namespace
        name: Dataset name
        max_depth: Maximum path depth for analysis
        
    Returns:
        Complexity metrics for upstream and downstream paths
    """
    path_finder = PathFinder(session)
    complexity_scorer = ComplexityScorer(session, path_finder)
    
    # Get upstream and downstream paths
    upstream_paths = path_finder.find_upstream_paths(
        namespace, name, max_depth=max_depth
    )
    downstream_paths = path_finder.find_downstream_paths(
        namespace, name, max_depth=max_depth
    )
    
    # Calculate complexity for all paths
    all_paths = upstream_paths + downstream_paths
    complexity_metrics = complexity_scorer.calculate_paths_complexity(all_paths)
    
    # Calculate aggregate metrics
    if complexity_metrics:
        avg_hop_count = sum(m["hop_count"] for m in complexity_metrics) / len(complexity_metrics)
        avg_transform_density = sum(m["transform_density"] for m in complexity_metrics) / len(complexity_metrics)
        max_hop_count = max(m["hop_count"] for m in complexity_metrics)
    else:
        avg_hop_count = 0.0
        avg_transform_density = 0.0
        max_hop_count = 0
    
    return {
        "dataset": {
            "namespace": namespace,
            "name": name
        },
        "path_count": len(all_paths),
        "upstream_path_count": len(upstream_paths),
        "downstream_path_count": len(downstream_paths),
        "aggregate_metrics": {
            "average_hop_count": round(avg_hop_count, 2),
            "average_transform_density": round(avg_transform_density, 2),
            "max_hop_count": max_hop_count
        },
        "path_complexity": complexity_metrics
    }


@app.get("/api/v1/redundancy/orphans")
async def get_orphan_datasets(
    session: Session = Depends(get_session)
):
    """Get list of orphan datasets (no upstream AND no downstream connections).
    
    Returns:
        List of orphan datasets with metadata
    """
    detector = RedundancyDetector(session)
    orphans = detector.find_orphan_datasets()
    
    return {
        "orphans": orphans,
        "count": len(orphans),
        "status": "candidates_for_deletion"
    }


@app.get("/api/v1/redundancy/duplicates")
async def get_duplicate_candidates(
    similarity_threshold: float = Query(default=0.7, ge=0.0, le=1.0, description="Minimum name similarity score"),
    path_overlap_threshold: float = Query(default=0.5, ge=0.0, le=1.0, description="Minimum path overlap score"),
    session: Session = Depends(get_session)
):
    """Get list of duplicate table candidates.
    
    Args:
        similarity_threshold: Minimum name similarity score (0.0-1.0)
        path_overlap_threshold: Minimum path overlap score (0.0-1.0)
        
    Returns:
        List of duplicate candidate groups
    """
    detector = RedundancyDetector(session)
    duplicates = detector.find_duplicate_candidates(
        similarity_threshold=similarity_threshold,
        path_overlap_threshold=path_overlap_threshold
    )
    
    return {
        "duplicate_groups": duplicates,
        "group_count": len(duplicates),
        "total_candidates": sum(g["count"] for g in duplicates),
        "status": "candidates_for_merging"
    }


@app.get("/api/v1/datasets/live")
async def get_live_datasets(
    days: Optional[int] = Query(default=None, ge=1, description="Filter by days since last access (e.g., 30)"),
    session: Session = Depends(get_session)
):
    """Get datasets with business usage ("live data").
    
    Args:
        days: Optional filter for datasets accessed within last N days
        
    Returns:
        List of datasets with business usage and access metrics
    """
    statement = select(FSDataset).where(FSDataset.access_count > 0)
    
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        statement = statement.where(FSDataset.last_accessed_at >= cutoff_date)
    
    datasets = session.exec(statement.order_by(FSDataset.last_accessed_at.desc())).all()
    
    return {
        "datasets": [
            {
                "namespace": d.namespace,
                "name": d.name,
                "layer": d.layer,
                "system": d.system,
                "access_count": d.access_count,
                "last_accessed_at": d.last_accessed_at.isoformat() if d.last_accessed_at else None
            }
            for d in datasets
        ],
        "count": len(datasets),
        "status": "live_data"
    }


@app.get("/api/v1/datasets/dead")
async def get_dead_datasets(
    days: int = Query(default=90, ge=1, description="Age threshold in days (datasets not accessed within this period)"),
    session: Session = Depends(get_session)
):
    """Get datasets without business usage ("dead data").
    
    Args:
        days: Age threshold - datasets not accessed within this period are considered dead
        
    Returns:
        List of datasets without business usage, sorted by last access (oldest first)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Datasets with no access OR last accessed before cutoff
    statement = select(FSDataset).where(
        (FSDataset.access_count == 0) | 
        (FSDataset.last_accessed_at < cutoff_date) |
        (FSDataset.last_accessed_at.is_(None))
    )
    
    datasets = session.exec(statement.order_by(FSDataset.last_accessed_at.asc().nulls_first())).all()
    
    return {
        "datasets": [
            {
                "namespace": d.namespace,
                "name": d.name,
                "layer": d.layer,
                "system": d.system,
                "access_count": d.access_count or 0,
                "last_accessed_at": d.last_accessed_at.isoformat() if d.last_accessed_at else None,
                "days_since_access": (
                    (datetime.utcnow() - d.last_accessed_at).days 
                    if d.last_accessed_at else None
                )
            }
            for d in datasets
        ],
        "count": len(datasets),
        "age_threshold_days": days,
        "status": "candidates_for_deprecation"
    }


@app.get("/api/v1/paths/business-critical")
async def get_business_critical_paths(
    namespace: Optional[str] = Query(default=None, description="Filter by dataset namespace"),
    dataset_name: Optional[str] = Query(default=None, description="Filter by dataset name"),
    max_depth: int = Query(default=20, ge=1, le=50, description="Maximum path depth"),
    from_layer: Optional[str] = Query(default=None, description="Filter by source layer (e.g., raw)"),
    to_layer: Optional[str] = Query(default=None, description="Filter by destination layer (e.g., bi)"),
    session: Session = Depends(get_session)
):
    """Get business-critical paths (paths that include datasets with business usage).
    
    Args:
        namespace: Optional dataset namespace to start from
        dataset_name: Optional dataset name to start from
        max_depth: Maximum path depth
        from_layer: Filter paths to start from this layer
        to_layer: Filter paths to end at this layer
        
    Returns:
        List of business-critical paths with business usage indicators
    """
    path_finder = PathFinder(session)
    
    if namespace and dataset_name:
        # Find paths for specific dataset
        paths = path_finder.find_filtered_paths(
            namespace, dataset_name,
            from_layer=from_layer,
            to_layer=to_layer,
            max_depth=max_depth,
            filter_business_only=True
        )
    else:
        # Find all business-critical paths (from all datasets with business usage)
        # Get all datasets with business usage
        statement = select(FSDataset).where(FSDataset.access_count > 0)
        live_datasets = session.exec(statement).all()
        
        paths = []
        for dataset in live_datasets:
            dataset_paths = path_finder.find_filtered_paths(
                dataset.namespace, dataset.name,
                from_layer=from_layer,
                to_layer=to_layer,
                max_depth=max_depth,
                filter_business_only=True
            )
            paths.extend(dataset_paths)
    
    # Get business usage indicators for all paths
    business_usage_indicators = [
        path_finder.get_path_business_usage_indicators(path) for path in paths
    ]
    
    return {
        "paths": paths,
        "count": len(paths),
        "paths_with_business_usage": [
            {
                "path": path,
                "business_usage": indicators,
                "is_business_critical": True
            }
            for path, indicators in zip(paths, business_usage_indicators)
        ],
        "status": "business_critical_paths"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

