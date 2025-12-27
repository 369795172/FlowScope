## Context

Phase 1 implements FlowScope's core analysis capabilities: synchronizing lineage data from Marquez and providing path analysis queries. This establishes the foundation for future phases (complexity scoring, redundancy detection, business usage integration).

**Stakeholders**: Development team, future users of FlowScope analysis features
**Constraints**:
- Must support both PostgreSQL (production) and SQLite (local development)
- Must use async patterns with FastAPI
- Must not modify Marquez (observational architecture)
- Must handle large lineage graphs efficiently

## Goals / Non-Goals

### Goals
- Synchronize lineage data from Marquez into FlowScope database
- Provide path query APIs (upstream/downstream from any dataset)
- Support enrichment fields (layer, system, domain, owner) for future analysis
- Establish reusable backend architecture for Phase 2+ features

### Non-Goals
- Complexity scoring or redundancy detection (Phase 2)
- Business usage tracking (Phase 3)
- Custom UI development (continue using Marquez UI for visualization)
- Real-time event streaming (poll-based sync is sufficient for Phase 1)

## Decisions

### Decision: Database Schema Design
**What**: Create four core tables: `fs_dataset`, `fs_job`, `fs_edge`, `fs_run` with enrichment fields.

**Schema outline**:
- `fs_dataset`: id, namespace, name, layer (raw/ods/dwd/dws/app/bi), system, domain, owner, created_at, updated_at
- `fs_job`: id, namespace, name, system, domain, owner, created_at, updated_at
- `fs_edge`: id, job_id, dataset_id, edge_type (input/output), created_at
- `fs_run`: id, job_id, run_id (from Marquez), state, started_at, completed_at, created_at

**Why**:
- Aligns with OpenLineage semantic model (Job, Dataset, Run, Input/Output)
- Enrichment fields (layer, system, domain, owner) support future analysis without schema changes
- Separate edge table enables efficient path traversal queries

**Alternatives considered**:
- Single denormalized table: Rejected - violates normalization, harder to query paths
- Graph database (Neo4j): Rejected - adds complexity, PostgreSQL/SQLite sufficient for Phase 1

### Decision: Sync Strategy
**What**: Poll Marquez API periodically (not real-time streaming) to fetch Jobs, Datasets, Runs, and Edges.

**Why**:
- Simpler implementation than event streaming
- Marquez API provides stable endpoints for querying lineage data
- Incremental sync (track last sync timestamp) minimizes API calls
- Sufficient for Phase 1 requirements

**Alternatives considered**:
- Direct database access to Marquez PostgreSQL: Rejected - couples FlowScope to Marquez internals, violates abstraction
- OpenLineage event streaming: Rejected - Phase 0 already emits to Marquez, sync from Marquez is cleaner separation

### Decision: Path Query Algorithm
**What**: Use NetworkX for DAG traversal and path enumeration, with cycle detection and path pruning for performance.

**Why**:
- NetworkX provides proven DAG algorithms (DFS, BFS, path enumeration)
- Handles cycles gracefully (important for real-world lineage graphs)
- Can optimize with path pruning (limit depth, filter by layer)
- Well-documented and maintained

**Alternatives considered**:
- Custom DAG traversal: Rejected - reinventing the wheel, NetworkX is battle-tested
- SQL recursive CTEs: Rejected - less flexible for complex path filtering, harder to optimize

### Decision: API Design
**What**: RESTful API with endpoints:
- `GET /api/v1/datasets/{namespace}/{name}/upstream` - All paths leading TO this dataset
- `GET /api/v1/datasets/{namespace}/{name}/downstream` - All paths leading FROM this dataset
- `GET /api/v1/datasets/{namespace}/{name}/paths?from_layer=raw&to_layer=bi` - Filtered paths

**Why**:
- RESTful design aligns with FastAPI conventions
- Clear, intuitive endpoint names
- Supports filtering via query parameters
- Returns JSON arrays of path objects (list of datasets/jobs in sequence)

**Alternatives considered**:
- GraphQL: Rejected - adds complexity, REST sufficient for Phase 1
- Single endpoint with complex query language: Rejected - over-engineered for Phase 1 needs

### Decision: Database Abstraction
**What**: Use SQLModel (SQLAlchemy + Pydantic) for type-safe models and database-agnostic code.

**Why**:
- SQLModel provides type safety (Pydantic models) + ORM (SQLAlchemy)
- Supports both PostgreSQL and SQLite without code changes
- Async support aligns with FastAPI async patterns
- Type hints improve code quality and IDE support

**Alternatives considered**:
- Raw SQLAlchemy: Rejected - SQLModel adds type safety without significant overhead
- Django ORM: Rejected - FastAPI ecosystem, SQLModel is lighter weight

## Risks / Trade-offs

### Risk: Large Lineage Graph Performance
**Risk**: Path queries on large graphs (thousands of nodes) may be slow or memory-intensive.

**Mitigation**:
- Implement path depth limits (e.g., max 20 hops)
- Add path pruning (stop at certain layers, filter early)
- Use database indexes on foreign keys (job_id, dataset_id)
- Consider pagination for path results if needed

### Risk: Sync Frequency and Data Freshness
**Risk**: Poll-based sync means lineage data may be stale between syncs.

**Mitigation**:
- Document sync frequency (e.g., every 5 minutes)
- Provide manual sync trigger endpoint for immediate updates
- Phase 2+ can add real-time sync if needed

### Risk: Marquez API Changes
**Risk**: Marquez API may change, breaking sync functionality.

**Mitigation**:
- Pin Marquez version in documentation
- Abstract Marquez client behind interface (easy to swap implementation)
- Test sync with Marquez version used in Phase 0

## Migration Plan

**N/A** - This is the first FlowScope backend implementation, no migration needed.

## Open Questions

- What should be the default sync frequency? (Recommendation: 5 minutes, configurable)
- Should path queries support pagination? (Recommendation: Yes, if paths exceed 100 results)
- How to handle deleted datasets/jobs in Marquez? (Recommendation: Mark as deleted, don't remove, for historical analysis)

