# Change: Implement Phase 3 Business Usage Integration

## Why

Phase 1 and Phase 2 provide path analysis and complexity metrics, but cannot distinguish between "data that exists" and "data that matters". Engineers need to identify which data paths are actively used by business applications (API calls, BI queries) versus data that exists but has no real business value. This enables data architecture decisions based on actual business usage patterns, not just lineage structure.

This change transforms FlowScope from a structural analysis tool into a business-value-aware system that can identify "live data" (actively used) versus "dead data" (unused), enabling informed decisions about what can be safely deprecated or removed.

## What Changes

- **New capability: `business-usage-tracking`**: Track dataset access from business-facing jobs (APIs, BI queries) and update access metrics
- **Modified capability: `flowspec-sync`**: Enhanced to detect business usage from job runs and update dataset access metrics (`access_count`, `last_accessed_at`)
- **Modified capability: `path-analysis`**: Enhanced to identify and highlight business-critical paths (paths with business usage)
- **New API endpoints**: 
  - Query "live data" (datasets with business usage)
  - Query "dead data" (datasets without business usage)
  - Get business-critical paths
- **Enhanced path queries**: Path responses include business usage indicators

**BREAKING**: None (additive changes only)

## Impact

- **New capabilities**: `business-usage-tracking`
- **Modified capabilities**: `flowspec-sync` (enhanced with usage tracking), `path-analysis` (enhanced with business indicators)
- **Affected specs**: `flowspec-sync` (modified), `path-analysis` (modified), `business-usage-tracking` (added)
- **Affected code**: 
  - `flowspec/sync/sync_service.py` (enhanced to track business usage)
  - New `flowspec/business_usage/` module (usage tracking logic)
  - `flowspec/path_analysis/path_finder.py` (enhanced with business indicators)
  - `flowspec/api/main.py` (new endpoints)
- **Dependencies**: No new external dependencies (uses existing OpenLineage events)











