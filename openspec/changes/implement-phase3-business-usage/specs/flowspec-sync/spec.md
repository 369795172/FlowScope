## MODIFIED Requirements

### Requirement: Marquez Data Synchronization
The system SHALL synchronize lineage data from Marquez into FlowScope database, including Jobs, Datasets, Runs, and Edges, and update business usage metrics for datasets.

#### Scenario: Sync jobs and datasets from Marquez
- **WHEN** sync service runs
- **THEN** all Jobs and Datasets from Marquez are fetched via API
- **AND** data is stored in FlowScope database (fs_job, fs_dataset tables)
- **AND** enrichment fields (layer, system, domain, owner) are preserved or set to defaults

#### Scenario: Sync runs and edges from Marquez
- **WHEN** sync service runs
- **THEN** all Runs and Edges from Marquez are fetched via API
- **AND** data is stored in FlowScope database (fs_run, fs_edge tables)
- **AND** relationships between Jobs, Datasets, and Runs are preserved

#### Scenario: Incremental sync
- **WHEN** sync service runs after a previous sync
- **THEN** only new or updated data since last sync is fetched
- **AND** last sync timestamp is tracked for efficient updates
- **AND** existing data is updated if changed in Marquez

#### Scenario: Update business usage metrics during sync
- **WHEN** sync service processes job runs from Marquez
- **THEN** business-facing jobs are detected (based on job name, system field, or output dataset layer)
- **AND** for each business job run, input datasets have their `access_count` incremented
- **AND** for each business job run, input datasets have their `last_accessed_at` updated to run completion time
- **AND** sync statistics include business usage update counts

### Requirement: Database Schema
The system SHALL provide database tables for storing lineage data with enrichment fields.

#### Scenario: Create database schema
- **WHEN** database is initialized
- **THEN** tables fs_dataset, fs_job, fs_edge, fs_run are created
- **AND** tables include enrichment fields (layer, system, domain, owner)
- **AND** foreign key relationships are established (job_id, dataset_id)
- **AND** fs_dataset table includes access metrics (access_count, last_accessed_at)

#### Scenario: Support multiple databases
- **WHEN** database type is configured (PostgreSQL or SQLite)
- **THEN** schema is created successfully
- **AND** ORM abstraction allows switching databases without code changes

### Requirement: Sync Error Handling
The system SHALL handle sync errors gracefully without losing data.

#### Scenario: Marquez API unavailable
- **WHEN** Marquez API is unavailable during sync
- **THEN** sync fails gracefully with error logging
- **AND** existing FlowScope data remains unchanged
- **AND** sync can be retried later

#### Scenario: Partial sync failure
- **WHEN** sync partially succeeds (some data fetched, some fails)
- **THEN** successfully fetched data is stored
- **AND** failed data is logged for retry
- **AND** sync status is recorded for debugging











