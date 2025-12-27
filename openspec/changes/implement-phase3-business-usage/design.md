# Design: Phase 3 Business Usage Integration

## Context

Phase 1 and Phase 2 provide structural analysis (path queries, complexity scoring, redundancy detection), but cannot answer: "Which data is actually used by business applications?" This is critical for data architecture decisions - engineers need to know what can be safely deprecated.

**Problem**: Without business usage tracking, FlowScope cannot distinguish between:
- **Live data**: Actively used by APIs, BI dashboards, business applications
- **Dead data**: Exists in lineage but has no recent business usage

**Goal**: Enable FlowScope to identify and highlight business-critical data paths based on actual usage patterns.

## Goals / Non-Goals

### Goals
- Track dataset access from business-facing jobs (APIs, BI queries, dashboards)
- Update dataset access metrics (`access_count`, `last_accessed_at`) automatically
- Provide API endpoints to query "live data" vs "dead data"
- Highlight business-critical paths in path analysis
- Enable data architecture decisions based on business usage patterns

### Non-Goals
- Real-time usage tracking (batch sync is sufficient)
- Detailed usage analytics (access count and last access time are sufficient)
- User-level access tracking (dataset-level is sufficient)
- Performance metrics (usage frequency is sufficient, not latency/throughput)

## Decisions

### Decision 1: Business Usage Detection Strategy

**Approach**: Detect business usage from job runs during sync, based on job characteristics:
- **Job naming convention**: Jobs with names containing `_api`, `_bi`, `_dashboard`, `_query`
- **Job system field**: Jobs with `system` field set to `api`, `bi`, `dashboard`
- **Dataset layer field**: Datasets with `layer` set to `bi` or `app` (business-facing layers)

**Rationale**: 
- Leverages existing OpenLineage events (no additional instrumentation needed)
- Uses existing enrichment fields (system, layer) that are already part of the model
- Flexible: supports multiple detection strategies (naming, system field, layer field)

**Alternatives considered**:
- Custom OpenLineage facets: Rejected - requires changes to all emitting systems
- Separate usage tracking API: Rejected - adds complexity, OpenLineage events are sufficient
- Manual annotation: Rejected - not scalable, defeats purpose of automated tracking

### Decision 2: Access Metrics Update Strategy

**Approach**: Update dataset access metrics when business job runs complete:
- When a business job run completes, update `access_count` and `last_accessed_at` for all input datasets
- Track both direct access (dataset is input to business job) and indirect access (dataset is upstream of business job)

**Rationale**:
- Captures both direct and indirect business usage
- Updates happen during sync (batch processing, no real-time requirement)
- Simple: increment counter and update timestamp

**Alternatives considered**:
- Track only direct access: Rejected - misses upstream datasets that are indirectly used
- Real-time updates: Rejected - adds complexity, batch sync is sufficient for Phase 3

### Decision 3: Business Usage Classification

**Approach**: Classify jobs as "business-facing" if they meet any of:
1. Job name contains business indicators: `_api`, `_bi`, `_dashboard`, `_query`, `_report`
2. Job `system` field is set to: `api`, `bi`, `dashboard`, `reporting`
3. Job outputs datasets with `layer` set to: `bi`, `app`

**Rationale**:
- Multiple detection strategies increase coverage
- Configurable: can be extended with additional patterns
- Conservative: errs on side of marking as business usage (better to over-detect than under-detect)

**Alternatives considered**:
- Single detection strategy: Rejected - too restrictive, misses edge cases
- Manual configuration file: Rejected - adds maintenance overhead, patterns are sufficient

### Decision 4: API Endpoint Design

**Approach**: Provide three new endpoints:
1. `GET /api/v1/datasets/live` - Datasets with business usage (access_count > 0)
2. `GET /api/v1/datasets/dead` - Datasets without business usage (access_count == 0 or last_accessed_at is old)
3. `GET /api/v1/paths/business-critical` - Paths that include business usage

**Rationale**:
- Simple, focused endpoints for common queries
- Reuses existing path analysis infrastructure
- Extensible: can add filters (time range, layer, etc.) later

**Alternatives considered**:
- Single endpoint with filters: Rejected - less intuitive, separate endpoints are clearer
- Complex query language: Rejected - overkill for Phase 3, simple endpoints are sufficient

## Risks / Trade-offs

### Risk 1: False Positives in Business Usage Detection
**Mitigation**: Use conservative patterns (err on side of marking as business usage), allow manual override via layer annotation

### Risk 2: Performance Impact of Access Metrics Updates
**Mitigation**: Batch updates during sync (not real-time), use database indexes on `access_count` and `last_accessed_at`

### Risk 3: Incomplete Coverage (Some Business Jobs Not Detected)
**Mitigation**: Support multiple detection strategies (naming, system field, layer field), document patterns for users

## Migration Plan

1. **No migration needed**: Additive changes only
2. **Existing datasets**: Will have `access_count=0` initially, will be updated on next sync if business usage detected
3. **Backward compatibility**: All existing APIs continue to work, new endpoints are additive

## Open Questions

- Should we track usage frequency (e.g., "accessed 100 times in last 30 days") or just last access time?
  - **Decision**: Start with simple metrics (access_count, last_accessed_at), can add frequency later if needed
- Should we distinguish between different types of business usage (API vs BI)?
  - **Decision**: Not in Phase 3, can add later if needed
- How to handle datasets that are used by both ETL and business jobs?
  - **Decision**: Mark as business usage if ANY business job uses it (conservative approach)











