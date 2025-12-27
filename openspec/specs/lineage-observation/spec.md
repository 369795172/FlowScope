## Purpose

FlowScope provides foundational lineage observation capabilities through OpenLineage events and Marquez visualization. This capability enables developers to observe real data lineage flows (job → dataset → job chains) without requiring analysis or judgment logic.

## Requirements

### Requirement: Marquez Local Deployment
The system SHALL provide a local Marquez deployment via Docker Compose that includes:
- Marquez API service for receiving OpenLineage events
- Marquez UI for lineage visualization
- PostgreSQL database for lineage storage
- All services accessible on localhost

#### Scenario: Start Marquez services
- **WHEN** developer runs `docker-compose up`
- **THEN** Marquez API, UI, and database services start successfully
- **AND** Marquez UI is accessible at http://localhost:3000 (or configured port)
- **AND** Marquez API is accessible at http://localhost:5000 (or configured port)

### Requirement: OpenLineage Event Emission
The system SHALL provide example ETL/API code that emits OpenLineage events to Marquez, demonstrating:
- Job execution events (JobRunStateChange)
- Dataset creation events (Dataset creation with schema)
- Input/Output relationships (Job inputs/outputs)

#### Scenario: ETL job emits lineage events
- **WHEN** example ETL script executes
- **THEN** OpenLineage events are emitted to Marquez API
- **AND** events include job name, dataset names, and input/output relationships
- **AND** events follow OpenLineage specification format

#### Scenario: API endpoint emits lineage events
- **WHEN** example API receives a request
- **THEN** OpenLineage events are emitted to Marquez API
- **AND** events link API response datasets to upstream data sources
- **AND** events follow OpenLineage specification format

### Requirement: Lineage Visualization
The system SHALL enable visualization of complete lineage chains in Marquez UI.

#### Scenario: View complete lineage chain
- **WHEN** developer navigates to Marquez UI after running example ETL/API
- **THEN** a complete lineage chain is visible showing: job → dataset → job
- **AND** nodes are clickable to view details
- **AND** edges show data flow direction
