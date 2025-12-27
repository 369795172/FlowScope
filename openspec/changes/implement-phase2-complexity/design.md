## Context

Phase 2 builds on Phase 1's path analysis capabilities to add judgment layer features that enable data architecture decision-making. Phase 1 provides path queries (upstream/downstream), but engineers need complexity metrics and redundancy detection to identify refactoring opportunities.

**Stakeholders**: Development team, engineers making data architecture decisions
**Constraints**:
- Must build on existing PathFinder infrastructure (NetworkX-based)
- Must support both PostgreSQL and SQLite (per project conventions)
- Must use async patterns with FastAPI
- Must not modify Marquez (observational architecture)
- Must handle large lineage graphs efficiently

## Goals / Non-Goals

### Goals
- Calculate and return complexity metrics for data paths (hop count, fan-in/out, transform density)
- Identify orphan datasets (no upstream or downstream connections)
- Identify duplicate intermediate table candidates (similar structure + overlapping paths)
- Provide refactoring recommendations (deletable/mergeable candidates)
- Enhance path query responses with complexity scores

### Non-Goals
- Automatic schema comparison for duplicate detection (manual annotation sufficient)
- Business usage tracking (Phase 3)
- Custom UI development (continue using Marquez UI or API responses)
- Automatic deletion or merging (all recommendations require human review)
- Real-time complexity updates (calculated on-demand)

## Decisions

### Decision: Complexity Scoring Algorithm
**What**: Calculate three complexity metrics for each path:
1. **Hop count**: Number of edges in the path (direct measure of path length)
2. **Fan-in/fan-out ratios**: Ratio of incoming to outgoing edges for nodes in the path
3. **Transform density**: Number of jobs (transforms) per dataset in the path

**Why**:
- Hop count provides simple, intuitive complexity measure
- Fan-in/out ratios identify nodes with high coupling (refactoring opportunities)
- Transform density identifies paths with many transformations (potential simplification targets)
- These metrics are computable from existing graph structure without additional data

**Alternatives considered**:
- Single complexity score: Rejected - multiple metrics provide richer insights
- Data volume-based complexity: Rejected - requires additional data not available in Phase 2
- Time-based complexity: Rejected - requires run history analysis (future enhancement)

### Decision: Orphan Dataset Detection Criteria
**What**: A dataset is considered an orphan if it has:
- No upstream connections (no input edges)
- AND no downstream connections (no output edges)

**Why**:
- Simple, unambiguous criteria
- Computable from existing graph structure
- Identifies datasets that are truly isolated (safe deletion candidates)

**Alternatives considered**:
- Only check upstream: Rejected - datasets with only downstream connections may still be valuable
- Include datasets with low usage: Rejected - requires usage tracking (Phase 3)

### Decision: Duplicate Table Identification Strategy
**What**: Identify duplicate candidates using:
1. **Name similarity**: Tables with similar names (e.g., `user_stats_v1`, `user_stats_v2`)
2. **Layer matching**: Tables in the same layer
3. **Path overlap**: Tables with overlapping upstream/downstream paths

**Why**:
- Name similarity is a strong heuristic for duplicates
- Layer matching ensures we compare tables at the same abstraction level
- Path overlap indicates functional similarity
- Does not require schema comparison (simpler, faster)

**Alternatives considered**:
- Schema comparison: Rejected - adds complexity, requires schema metadata not always available
- Exact name matching: Rejected - too restrictive, misses versioned tables
- Path overlap only: Rejected - may flag unrelated tables with coincidental path overlap

### Decision: API Design
**What**: RESTful API with endpoints:
- `GET /api/v1/datasets/{namespace}/{name}/complexity` - Complexity metrics for paths involving this dataset
- `GET /api/v1/redundancy/orphans` - List of orphan datasets
- `GET /api/v1/redundancy/duplicates` - List of duplicate table candidates
- Enhanced path query endpoints return complexity metrics in responses

**Why**:
- RESTful design aligns with FastAPI conventions
- Separate endpoints for redundancy detection enable batch analysis
- Complexity metrics in path responses provide immediate insights
- Clear, intuitive endpoint names

**Alternatives considered**:
- Single endpoint with query parameters: Rejected - less intuitive, harder to document
- GraphQL: Rejected - adds complexity, REST sufficient for Phase 2

### Decision: Complexity Calculation Caching
**What**: Cache complexity calculations per path to avoid recomputation.

**Why**:
- Complexity calculations can be expensive on large graphs
- Paths don't change frequently (only on sync)
- Caching improves API response times

**Alternatives considered**:
- No caching: Rejected - performance concerns on large graphs
- Full graph caching: Rejected - memory concerns, paths are sufficient

## Risks / Trade-offs

### Risk: Performance on Large Graphs
**Risk**: Complexity calculations on large graphs (thousands of nodes) may be slow.

**Mitigation**:
- Cache complexity calculations per path
- Limit path depth in calculations (use existing max_depth parameter)
- Use NetworkX's efficient graph algorithms
- Consider pagination for redundancy detection results if needed

### Risk: False Positives in Duplicate Detection
**Risk**: Duplicate detection may flag legitimate similar tables (e.g., intentionally versioned tables).

**Mitigation**:
- Use conservative similarity thresholds
- Require human review for all recommendations
- Provide context (paths, layers) to help engineers make decisions
- Allow manual exclusion of false positives

### Risk: Orphan Detection Misses Valuable Datasets
**Risk**: Some orphan datasets may be valuable (e.g., reference data, manually maintained tables).

**Mitigation**:
- Mark as "candidates" not "must delete"
- Require human review
- Provide dataset metadata (layer, owner, system) to help engineers make decisions

### Trade-off: Simplicity vs. Accuracy
**Trade-off**: Simple heuristics (name similarity, path overlap) may miss some duplicates but are fast and don't require schema metadata.

**Decision**: Favor simplicity - Phase 2 focuses on identifying candidates, not perfect accuracy. Engineers can refine recommendations based on domain knowledge.

## Migration Plan

**N/A** - This is an additive change. No migration needed.

## Open Questions

- What should be the default similarity threshold for duplicate detection? (Recommendation: 0.7 for name similarity, configurable)
- Should complexity scores be normalized (0-1 scale) or raw metrics? (Recommendation: Raw metrics with optional normalization)
- How to handle cycles in complexity calculations? (Recommendation: Use existing cycle detection from PathFinder)
- Should redundancy detection run on-demand or periodically? (Recommendation: On-demand via API, with optional background job for large graphs)












