## MODIFIED Requirements

### Requirement: Path Query Performance
The system SHALL optimize path queries for large lineage graphs and include complexity metrics in path responses.

#### Scenario: Limit path depth
- **WHEN** path query encounters very long paths (e.g., >20 hops)
- **THEN** path enumeration stops at depth limit
- **AND** partial paths are returned with depth indicator
- **AND** complexity metrics are calculated for returned paths

#### Scenario: Path pruning for efficiency
- **WHEN** path query processes large graph (thousands of nodes)
- **THEN** paths are pruned early based on filters (layer, system)
- **AND** query completes within reasonable time (<5 seconds for typical graphs)
- **AND** complexity metrics are included in path responses

## ADDED Requirements

### Requirement: Path Complexity Scoring
The system SHALL calculate and return complexity metrics for each path in path query responses.

#### Scenario: Path complexity calculation
- **WHEN** path query returns paths
- **THEN** each path includes complexity metrics (hop count, fan-in/out ratios, transform density)
- **AND** complexity metrics are calculated from the graph structure
- **AND** metrics are returned as part of the path response

#### Scenario: Complexity metrics for upstream paths
- **WHEN** API receives request for upstream paths of a dataset
- **THEN** all paths include complexity metrics
- **AND** paths can be optionally sorted by complexity score
- **AND** complexity metrics help identify refactoring opportunities

#### Scenario: Complexity metrics for downstream paths
- **WHEN** API receives request for downstream paths of a dataset
- **THEN** all paths include complexity metrics
- **AND** paths can be optionally sorted by complexity score
- **AND** complexity metrics help identify refactoring opportunities












