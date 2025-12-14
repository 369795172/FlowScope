# Project Context

## Purpose

FlowScope is a data lineage observation and analysis tool designed to help engineers make data architecture decisions based on real runtime data flows. Unlike traditional lineage tools that focus on visualization, FlowScope emphasizes **actionable insights** for architecture judgment and refactoring decisions.

**Core Mission**: Enable engineers to understand, analyze, and make informed decisions about their data architecture through observation of actual data flow patterns, not just static diagrams.

**Key Differentiators**:
- **Real runtime data flows**: Observes actual execution patterns, not just static definitions
- **Architecture decision support**: Provides complexity metrics, redundancy detection, and path analysis to guide refactoring
- **Lightweight and local-first**: Designed to run on personal development machines without cloud dependencies
- **Observational approach**: Does not replace ETL or scheduling tools; only observes and analyzes

**Success Criteria**: The system must enable engineers to answer:
1. **Traceability**: Trace any BI table/API/decision metric back to all raw data sources with complete paths
2. **Complexity awareness**: Quantify data path complexity (length, node count, fan-in/out)
3. **Redundancy identification**: Identify orphan tables, duplicate intermediate tables, and unused datasets
4. **Business perspective**: Distinguish between "exists but unused" data and "high-frequency business-critical" paths
5. **Local usability**: Run efficiently on personal development machines with controlled resource usage

## Tech Stack

### Infrastructure
- **OpenLineage**: Event standard for data lineage events (Job/Dataset/Run/Input/Output semantic model)
- **Marquez**: Lineage fact storage and basic visualization (Docker Compose local deployment)

### Backend
- **Language**: Python
- **Web Framework**: FastAPI (async-first patterns)
- **ORM**: SQLAlchemy / SQLModel (type-safe models)
- **Database**: PostgreSQL (production) or SQLite (local-only development)
- **Graph Analysis**: NetworkX or custom DAG algorithms for path enumeration and complexity scoring

### Frontend
- **Phase 0-1**: Reuse Marquez UI for initial lineage visualization
- **Phase 2+ (Optional)**: React + D3.js / Cytoscape.js for custom visualization focused on path highlighting and risk indicators

## Project Conventions

### Code Style
- **Python conventions**: Follow PEP 8 style guidelines
- **Type safety**: Use type hints throughout; leverage SQLModel for type-safe database models
- **Async-first**: Prefer async/await patterns with FastAPI
- **Naming**: Use descriptive names that reflect domain concepts (Job, Dataset, Run, Edge, Path)

### Architecture Patterns

**Separation of Concerns**:
- **Fact Layer** (OpenLineage + Marquez): Records "what happened" - pure observation, no analysis
- **Judgment Layer** (FlowScope): Provides "what it means / what to do" - analysis, scoring, recommendations

**Observational Architecture**:
- FlowScope does **not** execute or manage ETL jobs
- FlowScope does **not** replace task schedulers (Airflow/Dagster)
- FlowScope **only** observes and analyzes existing data flows

**Modular Design**:
1. **FlowScope Sync**: Synchronizes data from Marquez, enriches with engineering/business semantics
2. **Path Analysis Engine**: DAG path enumeration, complexity scoring, main path identification
3. **Redundancy & Risk Detection**: Orphan detection, duplicate table identification, path complexity warnings
4. **Business Usage Integration**: Lightweight API/BI query instrumentation to mark real business-touched data paths

**Data Layer Abstraction**:
- Support both PostgreSQL (production) and SQLite (local development)
- Database schema: `fs_dataset`, `fs_job`, `fs_edge`, `fs_run` tables
- ORM abstraction allows switching databases without code changes

### Testing Strategy

**Status**: Testing approach TBD

**Planned Focus Areas**:
- Integration testing with Marquez (event emission and sync)
- Path analysis algorithm correctness (DAG traversal, complexity calculations)
- API endpoint testing (upstream/downstream path queries)
- Data model validation (layer classification, edge relationships)

**Testing Philosophy**: Prioritize integration tests that validate the observational pipeline end-to-end, ensuring FlowScope correctly interprets and enriches lineage data from Marquez.

### Git Workflow

**Status**: Git workflow TBD

**Recommended Approach** (to be confirmed):
- Feature branches for new modules or significant enhancements
- Main branch for stable, tested code
- Commit messages should reference phase numbers (Phase 0, Phase 1, etc.) when applicable

## Domain Context

### Data Lineage Concepts

**Core Entities**:
- **Job**: A data transformation or processing task (ETL job, API endpoint, ML model training)
- **Dataset**: A data artifact (table, file, API response) that is input to or output from Jobs
- **Run**: A single execution instance of a Job
- **Edge**: A relationship between Job and Dataset (input or output)
- **Path**: A sequence of Jobs and Datasets from source to destination

**Layer Classification** (manual annotation):
- `raw`: Raw source data
- `ods`: Operational Data Store
- `dwd`: Data Warehouse Detail
- `dws`: Data Warehouse Summary
- `app`: Application layer
- `bi`: Business Intelligence / Reporting layer

**Path Analysis Concepts**:
- **Upstream**: All paths leading TO a dataset (sources)
- **Downstream**: All paths leading FROM a dataset (destinations)
- **Path complexity**: Measured by hop count, fan-in/out ratios, transform density
- **Main path**: The most frequently used or highest-volume path through the data flow
- **Orphan dataset**: A dataset with no upstream or downstream connections
- **Duplicate intermediate table**: Multiple tables with similar structure and overlapping upstream/downstream paths

**Business Value Mapping**:
- **Live data**: Data paths that are actively used by business applications (API calls, BI queries)
- **Dead data**: Data paths that exist but have no recent business usage
- **Critical path**: High-frequency, high-importance data flows that business operations depend on

### Data Architecture Analysis Goals

1. **Traceability**: Given any output (BI table, API, metric), trace back to all raw data sources
2. **Complexity Quantification**: Measure and score path complexity to identify refactoring opportunities
3. **Redundancy Detection**: Identify datasets that can be safely deleted or merged
4. **Usage-Based Prioritization**: Distinguish between infrastructure that exists vs. infrastructure that matters

## Important Constraints

### Technical Constraints

- **Local-first deployment**: Must run efficiently on personal development machines
- **Resource efficiency**: Controlled resource usage; cannot require cloud infrastructure
- **Database flexibility**: Must support both PostgreSQL and SQLite for different deployment scenarios
- **Observational only**: Cannot execute, schedule, or manage ETL jobs

### Functional Boundaries (Explicit Non-Goals)

- **No task scheduling**: Does not replace Airflow, Dagster, or other orchestration tools
- **No enterprise governance**: Does not provide permissions, approvals, audit trails, or compliance features
- **No automatic semantic understanding**: Layer/domain classification is manual annotation, not automatic schema analysis
- **No execution management**: Does not trigger, monitor, or control data pipeline execution

### Design Philosophy Constraints

- **Fact vs. Judgment separation**: Keep pure observation (Marquez) separate from analysis (FlowScope)
- **Minimal disruption**: FlowScope should integrate via OpenLineage events without requiring changes to existing ETL code
- **Progressive enhancement**: Start with basic path queries, add complexity analysis incrementally

## External Dependencies

### Core Dependencies

- **OpenLineage**: 
  - Purpose: Standard event format for data lineage
  - Integration: ETL jobs/APIs emit OpenLineage events
  - Version: Latest stable (check compatibility with Marquez)

- **Marquez**: 
  - Purpose: Lineage fact storage and basic DAG visualization
  - Deployment: Docker Compose for local development
  - Role: Acts as "lineage fact database" and debugging tool
  - Integration: FlowScope syncs data from Marquez API/database

### Supporting Libraries

- **NetworkX** (or custom DAG algorithms):
  - Purpose: Graph analysis for path enumeration and complexity calculations
  - Usage: DAG traversal, path finding, graph metrics (fan-in/out, centrality)

- **PostgreSQL** (optional):
  - Purpose: Production database for FlowScope enhanced layer
  - Alternative: SQLite for local-only deployments

- **FastAPI**:
  - Purpose: Web framework for FlowScope API endpoints
  - Features: Async support, automatic OpenAPI documentation

- **SQLModel / SQLAlchemy**:
  - Purpose: ORM for database abstraction and type-safe models
  - Benefits: Database-agnostic code, type safety

### Future Dependencies (Phase 2+)

- **React + D3.js / Cytoscape.js** (optional):
  - Purpose: Custom visualization for path highlighting and risk indicators
  - Note: Only if moving beyond Marquez UI
