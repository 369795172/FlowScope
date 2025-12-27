# path-analysis Specification

## Purpose
TBD - created by archiving change implement-phase1-sync. Update Purpose after archive.
## Requirements
### Requirement: Upstream Path Query
The system SHALL provide an API endpoint to query all upstream paths (sources) leading to a given dataset.

#### Scenario: Query upstream paths for a dataset
- **WHEN** API receives request for upstream paths of a dataset
- **THEN** all paths from raw data sources to the dataset are returned
- **AND** each path is a sequence of datasets and jobs (e.g., [raw.users, etl_job, processed.users])
- **AND** paths are returned as JSON array

#### Scenario: Filter upstream paths by layer
- **WHEN** API receives request with layer filter (e.g., from_layer=raw)
- **THEN** only paths starting from specified layer are returned
- **AND** paths are filtered before enumeration for performance

#### Scenario: Handle cycles in lineage graph
- **WHEN** lineage graph contains cycles (circular dependencies)
- **THEN** path enumeration detects cycles and prevents infinite loops
- **AND** paths are returned up to cycle detection point

### Requirement: Downstream Path Query
The system SHALL provide an API endpoint to query all downstream paths (destinations) from a given dataset.

#### Scenario: Query downstream paths for a dataset
- **WHEN** API receives request for downstream paths of a dataset
- **THEN** all paths from the dataset to destination datasets are returned
- **AND** each path is a sequence of datasets and jobs
- **AND** paths are returned as JSON array

#### Scenario: Filter downstream paths by layer
- **WHEN** API receives request with layer filter (e.g., to_layer=bi)
- **THEN** only paths ending at specified layer are returned
- **AND** paths are filtered before enumeration for performance

### Requirement: Path Query Performance
The system SHALL optimize path queries for large lineage graphs.

#### Scenario: Limit path depth
- **WHEN** path query encounters very long paths (e.g., >20 hops)
- **THEN** path enumeration stops at depth limit
- **AND** partial paths are returned with depth indicator

#### Scenario: Path pruning for efficiency
- **WHEN** path query processes large graph (thousands of nodes)
- **THEN** paths are pruned early based on filters (layer, system)
- **AND** query completes within reasonable time (<5 seconds for typical graphs)

### Requirement: Acceptance Criteria Validation
The system SHALL meet Phase 1 acceptance criteria: given a BI table, output all raw → BI path lists.

#### Scenario: Query paths from raw to BI
- **WHEN** API receives request for paths from raw layer to BI layer for a specific dataset
- **THEN** all complete paths from raw data sources to the BI dataset are returned
- **AND** paths include all intermediate datasets and jobs
- **AND** paths are complete and traceable end-to-end

