# FlowScope - Phase 0 MVP

FlowScope is a data lineage observation and analysis tool. Phase 0 establishes the foundational infrastructure for observing data lineage flows through OpenLineage events and Marquez.

## Overview

Phase 0 demonstrates that we can observe real data lineage flows through:
- **Marquez**: Local deployment for lineage storage and visualization
- **OpenLineage Events**: Standard events emitted from ETL/API code
- **Lineage Visualization**: Complete job → dataset → job chains visible in Marquez UI

## Integration Guide

**Want to integrate FlowScope into your project?** 

📖 See [**INTEGRATION_SOP.md**](INTEGRATION_SOP.md) for a complete step-by-step guide on:
- Setting up FlowScope infrastructure
- Integrating OpenLineage events into your ETL/API code
- Verification and troubleshooting
- Best practices and common patterns

The SOP document provides ready-to-use code examples for ETL tasks, API services, and common integration scenarios.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ installed
- `pip` for installing Python dependencies

## Quick Start

### 1. Start Marquez Services

Start Marquez using Docker Compose:

```bash
docker-compose up -d
```

This starts three services:
- **PostgreSQL**: Database for lineage storage (port 5432)
- **Marquez API**: Receives OpenLineage events (port 5002, mapped from container port 5000)
- **Marquez Web UI**: Lineage visualization (port 3000)

Wait for services to be healthy (about 30 seconds), then verify:

```bash
# Check API health (using /api/v1/namespaces endpoint)
curl http://localhost:5002/api/v1/namespaces

# Check Web UI
curl http://localhost:3000
```

### 2. Install Python Dependencies

Create a virtual environment and install the OpenLineage Python client:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r examples/requirements.txt
```

### 3. Run Example Scripts

Set the Marquez URL (optional, defaults to http://localhost:5002):

```bash
export MARQUEZ_URL=http://localhost:5002
```

Run the ETL example (make sure virtual environment is activated):

```bash
source venv/bin/activate  # If not already activated
python examples/etl_example.py
```

This creates a lineage chain: `raw.users` → `user_processing_etl` → `processed.users`

Run the API example:

```bash
python examples/api_example.py
```

This extends the lineage chain: `processed.users` → `user_stats_api` → `user_stats`

### 4. View Lineage in Marquez UI

1. Open your browser and navigate to: http://localhost:3000
2. Search for datasets or jobs:
   - `raw.users`
   - `processed.users`
   - `user_processing_etl`
   - `user_stats_api`
3. Click on any dataset or job to view its lineage graph
4. You should see a complete chain: `raw.users` → `user_processing_etl` → `processed.users` → `user_stats_api` → `user_stats`

## Verification Checklist

- [ ] Marquez services start successfully (`docker-compose ps` shows all services as "healthy")
- [ ] Marquez API is accessible at http://localhost:5002
- [ ] Marquez UI is accessible at http://localhost:3000
- [ ] ETL example runs and emits events successfully
- [ ] API example runs and emits events successfully
- [ ] Complete lineage chain is visible in Marquez UI (job → dataset → job)

## OpenLineage Event Structure

The example scripts emit OpenLineage events following the standard specification:

### Event Types

- **START**: Emitted when a job begins execution
- **COMPLETE**: Emitted when a job finishes successfully

### Event Components

Each event includes:

1. **Job**: Identifies the transformation/processing task
   - `namespace`: Logical grouping (e.g., "flowspec_examples")
   - `name`: Job identifier (e.g., "user_processing_etl")

2. **Run**: Identifies a specific execution instance
   - `runId`: Unique UUID for this execution

3. **Datasets**: Input and output data artifacts
   - `namespace`: Data source identifier (e.g., "postgresql://localhost:5432")
   - `name`: Dataset name (e.g., "raw.users")
   - `facets`: Metadata including schema definitions

4. **Schema Facets**: Describe dataset structure
   - `fields`: Array of `SchemaField` objects with `name` and `type`

### Example Event Flow

**ETL Job Event**:
```python
RunEvent(
    eventType=RunState.COMPLETE,
    run=Run(runId="..."),
    job=Job(namespace="flowspec_examples", name="user_processing_etl"),
    inputs=[Dataset(namespace="postgresql://...", name="raw.users")],
    outputs=[Dataset(namespace="postgresql://...", name="processed.users")]
)
```

**API Job Event**:
```python
RunEvent(
    eventType=RunState.COMPLETE,
    run=Run(runId="..."),
    job=Job(namespace="flowspec_examples", name="user_stats_api"),
    inputs=[Dataset(namespace="postgresql://...", name="processed.users")],
    outputs=[Dataset(namespace="api://...", name="user_stats")]
)
```

This creates a lineage chain: `raw.users` → `user_processing_etl` → `processed.users` → `user_stats_api` → `user_stats`

## Resource Requirements

- **Docker**: ~500MB disk space for images
- **Memory**: ~1GB RAM for Marquez services
- **CPU**: Minimal (suitable for local development)

## Troubleshooting

### Marquez services won't start

- Check Docker is running: `docker ps`
- Check ports are available: `lsof -i :5000`, `lsof -i :3000`, `lsof -i :5432`
- View logs: `docker-compose logs`

### Events not appearing in UI

- Verify Marquez API is healthy: `curl http://localhost:5002/api/v1/namespaces`
- Check event emission succeeded (scripts print confirmation)
- Refresh Marquez UI and search for job/dataset names
- Check Marquez API logs: `docker-compose logs marquez-api`

### Python import errors

- Ensure dependencies are installed: `pip install -r examples/requirements.txt`
- Verify Python version: `python --version` (should be 3.8+)

## Stopping Services

Stop Marquez services:

```bash
docker-compose down
```

To remove data volumes (clean slate):

```bash
docker-compose down -v
```

## Next Steps

Phase 0 establishes the observational foundation. Future phases will add:
- **Phase 1**: FlowScope Sync and path analysis
- **Phase 2**: Complexity and redundancy detection
- **Phase 3**: Business usage integration

## References

- [OpenLineage Specification](https://openlineage.io/docs)
- [Marquez Documentation](https://marquezproject.github.io/marquez/)
- [OpenLineage Python Client](https://openlineage.io/docs/client/python)
