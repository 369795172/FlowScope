## 1. Database Schema and Models
- [x] 1.1 Create database models using SQLModel (fs_dataset, fs_job, fs_edge, fs_run)
- [x] 1.2 Add enrichment fields (layer, system, domain, owner, activity metrics)
- [x] 1.3 Create database migration/initialization script
- [x] 1.4 Support both PostgreSQL and SQLite (per project conventions)

## 2. FlowScope Sync Module
- [x] 2.1 Implement Marquez API client for fetching Jobs, Datasets, Runs, Edges
- [x] 2.2 Create sync service that maps Marquez data to FlowScope models
- [x] 2.3 Implement incremental sync (track last sync timestamp)
- [x] 2.4 Handle sync errors and retries gracefully

## 3. Path Analysis Engine
- [x] 3.1 Implement DAG path enumeration algorithm (upstream/downstream traversal)
- [x] 3.2 Create path query service that returns all paths from/to a dataset
- [x] 3.3 Optimize path queries for large graphs (path pruning, cycle detection)
- [x] 3.4 Add path filtering by layer (e.g., find all raw → bi paths)

## 4. FastAPI Backend
- [x] 4.1 Create FastAPI application structure
- [x] 4.2 Implement database connection and session management
- [x] 4.3 Create API endpoints for path queries (upstream/downstream)
- [x] 4.4 Add OpenAPI documentation
- [x] 4.5 Implement health check endpoint

## 5. Testing and Validation
- [x] 5.1 Test sync with real Marquez data (from Phase 0 examples)
- [x] 5.2 Verify path queries return correct results for known lineage chains
- [x] 5.3 Test with both PostgreSQL and SQLite databases
- [x] 5.4 Validate acceptance criteria: given a BI table, output all raw → BI paths

