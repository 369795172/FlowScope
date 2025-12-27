# FlowScope Phase 1 - Implementation Guide

Phase 1 implements FlowScope's core analysis capabilities: synchronizing lineage data from Marquez and providing path analysis queries.

## Setup

### 1. Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
# Initialize database (creates tables)
python scripts/init_db.py
```

By default, this uses SQLite (`flowspec.db`). To use PostgreSQL:

```bash
export DB_TYPE=postgresql
export DB_USER=marquez
export DB_PASSWORD=marquez
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=flowspec
python scripts/init_db.py
```

### 3. Start Marquez (if not already running)

```bash
docker-compose up -d
```

Wait for services to be healthy, then verify:

```bash
curl http://localhost:5002/api/v1/namespaces
```

### 4. Run Example ETL/API (to populate Marquez with lineage data)

```bash
# Set Marquez URL
export MARQUEZ_URL=http://localhost:5002

# Run examples
python examples/etl_example.py
python examples/api_example.py
```

## Usage

### Sync Data from Marquez

```bash
# Sync all lineage data from Marquez to FlowScope
python scripts/sync_marquez.py
```

This will:
- Fetch all namespaces, jobs, datasets, runs, and edges from Marquez
- Store them in FlowScope database
- Print sync statistics

### Start API Server

```bash
# Start FlowScope API server
python scripts/run_api.py
```

The API will be available at:
- API: http://localhost:8000
- OpenAPI docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Query Paths

#### Get upstream paths (sources)

```bash
# Get all upstream paths for a dataset
curl "http://localhost:8000/api/v1/datasets/postgresql%3A%2F%2Flocalhost%3A5432/user_stats/upstream"

# Filter by source layer (e.g., raw)
curl "http://localhost:8000/api/v1/datasets/postgresql%3A%2F%2Flocalhost%3A5432/user_stats/upstream?from_layer=raw"
```

#### Get downstream paths (destinations)

```bash
# Get all downstream paths from a dataset
curl "http://localhost:8000/api/v1/datasets/postgresql%3A%2F%2Flocalhost%3A5432/raw.users/downstream"

# Filter by destination layer (e.g., bi)
curl "http://localhost:8000/api/v1/datasets/postgresql%3A%2F%2Flocalhost%3A5432/raw.users/downstream?to_layer=bi"
```

#### Get filtered paths (raw → bi)

```bash
# Get all paths from raw to bi for a dataset
curl "http://localhost:8000/api/v1/datasets/postgresql%3A%2F%2Flocalhost%3A5432/user_stats/paths?from_layer=raw&to_layer=bi"
```

## Project Structure

```
flowspec/
├── models/          # Database models (FSDataset, FSJob, FSEdge, FSRun)
├── db/              # Database configuration and initialization
├── sync/            # Marquez sync service
├── path_analysis/   # Path finding algorithms
└── api/             # FastAPI application

scripts/
├── init_db.py       # Database initialization script
├── sync_marquez.py  # Sync script
└── run_api.py       # API server entry point
```

## Acceptance Criteria Validation

To validate Phase 1 acceptance criteria ("given a BI table, output all raw → BI paths"):

1. Ensure you have lineage data in Marquez (run examples)
2. Sync data: `python scripts/sync_marquez.py`
3. Query paths: Use the `/paths` endpoint with `from_layer=raw&to_layer=bi`

Example:

```bash
# Assuming user_stats is a BI table
curl "http://localhost:8000/api/v1/datasets/api%3A%2F%2Flocalhost%3A8000/user_stats/paths?from_layer=raw&to_layer=bi"
```

This should return all complete paths from raw data sources to the BI dataset.

## Next Steps

Phase 1 implementation is complete. Future phases will add:
- **Phase 2**: Complexity scoring and redundancy detection
- **Phase 3**: Business usage integration









