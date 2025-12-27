# Change: Implement Phase 2 Complexity and Redundancy Detection

## Why

Phase 1 provides path queries that enable engineers to trace data flows, but lacks analysis capabilities to guide refactoring decisions. Engineers need complexity metrics and redundancy detection to identify what can be safely deleted or merged, enabling data architecture judgment and refactoring decisions based on actual lineage patterns.

This change transforms FlowScope from a path query tool into an analysis engine that provides actionable insights for data architecture decisions.

## What Changes

- **New capability: `complexity-scoring`**: Path complexity metrics (hop count, fan-in/out ratios, transform density) to quantify data path complexity
- **New capability: `redundancy-detection`**: Orphan dataset detection and duplicate intermediate table identification to identify refactoring opportunities
- **Modified capability: `path-analysis`**: Enhanced with complexity scoring in path query responses
- **New API endpoints**: Complexity scoring and redundancy detection endpoints for programmatic access
- **Enhanced path queries**: Path responses include complexity metrics for each path

**BREAKING**: None (additive changes only)

## Impact

- **New capabilities**: `complexity-scoring`, `redundancy-detection`
- **Modified capabilities**: `path-analysis` (enhanced with complexity metrics)
- **Affected specs**: `path-analysis` (modified), `redundancy-detection` (added)
- **Affected code**: 
  - `flowspec/path_analysis/` (enhanced)
  - New `flowspec/complexity/` module
  - New `flowspec/redundancy/` module
  - `flowspec/api/` (new endpoints)
- **Dependencies**: NetworkX (already used), no new external dependencies












