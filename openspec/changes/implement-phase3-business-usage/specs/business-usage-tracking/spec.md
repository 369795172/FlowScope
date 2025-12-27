## ADDED Requirements

### Requirement: Business Usage Detection
The system SHALL detect business-facing jobs (APIs, BI queries, dashboards) and track their usage of datasets.

#### Scenario: Detect API job as business usage
- **WHEN** a job run completes and the job name contains `_api` or `_query`
- **THEN** the job is classified as business-facing
- **AND** all input datasets are marked as having business usage

#### Scenario: Detect BI job as business usage
- **WHEN** a job run completes and the job `system` field is set to `bi` or `dashboard`
- **THEN** the job is classified as business-facing
- **AND** all input datasets are marked as having business usage

#### Scenario: Detect business usage from dataset layer
- **WHEN** a job outputs a dataset with `layer` set to `bi` or `app`
- **THEN** the job is classified as business-facing
- **AND** all input datasets are marked as having business usage

### Requirement: Dataset Access Metrics Update
The system SHALL update dataset access metrics (`access_count`, `last_accessed_at`) when business jobs access datasets.

#### Scenario: Update access metrics for direct usage
- **WHEN** a business job run completes with a dataset as input
- **THEN** the dataset's `access_count` is incremented
- **AND** the dataset's `last_accessed_at` is updated to the run completion time

#### Scenario: Update access metrics for multiple business jobs
- **WHEN** multiple business job runs access the same dataset
- **THEN** the dataset's `access_count` reflects the total number of business accesses
- **AND** the dataset's `last_accessed_at` reflects the most recent business access

#### Scenario: Track access during sync
- **WHEN** sync service processes job runs from Marquez
- **THEN** business usage is detected and access metrics are updated
- **AND** sync statistics include business usage update counts

### Requirement: Live Data Query
The system SHALL provide an API endpoint to query datasets with business usage ("live data").

#### Scenario: Query live datasets
- **WHEN** a client requests live datasets via `GET /api/v1/datasets/live`
- **THEN** all datasets with `access_count > 0` are returned
- **AND** results include access metrics (access_count, last_accessed_at)

#### Scenario: Filter live datasets by time range
- **WHEN** a client requests live datasets with a time range filter
- **THEN** only datasets accessed within the time range are returned
- **AND** results are sorted by last_accessed_at (most recent first)

### Requirement: Dead Data Query
The system SHALL provide an API endpoint to query datasets without business usage ("dead data").

#### Scenario: Query dead datasets
- **WHEN** a client requests dead datasets via `GET /api/v1/datasets/dead`
- **THEN** all datasets with `access_count == 0` or `last_accessed_at` older than threshold are returned
- **AND** results are marked as candidates for deprecation

#### Scenario: Filter dead datasets by age
- **WHEN** a client requests dead datasets with an age threshold (e.g., 90 days)
- **THEN** only datasets not accessed within the threshold are returned
- **AND** results are sorted by last_accessed_at (oldest first)

### Requirement: Business-Critical Path Identification
The system SHALL identify and highlight paths that include business usage.

#### Scenario: Identify business-critical paths
- **WHEN** a client requests paths for a dataset
- **THEN** paths that include datasets with business usage are marked as business-critical
- **AND** path responses include business usage indicators

#### Scenario: Filter paths by business usage
- **WHEN** a client requests paths with business usage filter
- **THEN** only paths that include business usage are returned
- **AND** results highlight which datasets in the path have business usage











