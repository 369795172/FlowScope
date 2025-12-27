# Change: Setup Phase 0 MVP - Lineage Observation Foundation

## Why

FlowScope needs a working observational foundation before building analysis capabilities. Phase 0 validates that OpenLineage events can be captured and visualized through Marquez, proving the architectural approach of separating the "fact layer" (Marquez) from the "judgment layer" (future FlowScope enhancements). This MVP establishes that we can observe real data lineage flows without building any analysis logic yet.

## What Changes

- Add Marquez deployment via Docker Compose for local development
- Add example ETL/API code that emits OpenLineage events to Marquez
- Add documentation for running the MVP locally and verifying lineage visualization
- Establish minimal project structure for Python backend (foundation for future phases)

## Impact

- **New capability**: `lineage-observation` - Core capability for observing data lineage flows
- **New infrastructure**: Docker Compose configuration for Marquez services (API, UI, PostgreSQL)
- **New code**: Example OpenLineage event emitters demonstrating job → dataset → job lineage chains
- **Affected specs**: None (this is the initial capability)
- **Affected code**: New files only (no existing code to modify)
