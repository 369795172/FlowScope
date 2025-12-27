# Change: Implement Phase 1 Sync - FlowScope Analysis Foundation

## Why

Phase 0 established that we can observe data lineage flows through OpenLineage events and Marquez. However, Marquez only provides basic visualization and fact storage. Phase 1 adds FlowScope's core analysis capabilities: synchronizing lineage data from Marquez into FlowScope's enhanced data model, and providing path analysis queries that enable engineers to answer questions like "Given a BI table, what are all paths from raw data sources?"

This change transforms FlowScope from a pure observation tool into an analysis engine that supports data architecture decision-making.

## What Changes

- **New capability: `flowspec-sync`**: Synchronizes Job, Dataset, Run, and Edge data from Marquez into FlowScope database
- **New capability: `path-analysis`**: Provides upstream/downstream path query APIs for tracing data flows
- **Database schema**: Creates `fs_dataset`, `fs_job`, `fs_edge`, `fs_run` tables with enrichment fields (layer, system, domain, owner)
- **FastAPI backend**: Establishes FlowScope backend service with async patterns
- **Path query API**: Implements endpoints for querying upstream/downstream paths from any dataset

**BREAKING**: None (this is the first FlowScope backend implementation)

## Impact

- **New capabilities**: `flowspec-sync`, `path-analysis`
- **New infrastructure**: FlowScope backend service, database schema
- **Affected specs**: None (new capabilities)
- **Affected code**: New backend codebase (no existing code to modify)
- **Dependencies**: FastAPI, SQLModel, NetworkX (or custom DAG algorithms), Marquez API client

