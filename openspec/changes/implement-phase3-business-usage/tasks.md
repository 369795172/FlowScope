## 1. Business Usage Detection Module

- [x] 1.1 Create business usage detector (`flowspec/business_usage/usage_tracker.py`)
- [x] 1.2 Implement job type detection (identify business-facing jobs: API, BI, dashboard)
- [x] 1.3 Implement business usage detection logic (check job names, system field, layer field)
- [x] 1.4 Create business usage classification service

## 2. Sync Service Enhancement

- [x] 2.1 Enhance `sync_service.py` to detect business usage from job runs
- [x] 2.2 Update dataset `access_count` when business job runs complete
- [x] 2.3 Update dataset `last_accessed_at` when business job runs complete
- [x] 2.4 Track business usage for input datasets (datasets consumed by business jobs)
- [x] 2.5 Add business usage metrics to sync statistics

## 3. Path Analysis Enhancement

- [x] 3.1 Enhance `path_finder.py` to include business usage indicators in paths
- [x] 3.2 Add business-critical path identification (paths with business usage)
- [x] 3.3 Add business usage metadata to path query responses
- [x] 3.4 Filter paths by business usage (e.g., only show paths with business usage)

## 4. API Endpoints

- [x] 4.1 Create "live data" endpoint (`GET /api/v1/datasets/live`)
- [x] 4.2 Create "dead data" endpoint (`GET /api/v1/datasets/dead`)
- [x] 4.3 Create business-critical paths endpoint (`GET /api/v1/paths/business-critical`)
- [x] 4.4 Enhance existing path endpoints to include business usage indicators
- [x] 4.5 Add OpenAPI documentation for new endpoints

## 5. Testing and Validation

- [x] 5.1 Test business usage detection with API job runs (verify access metrics updated)
- [x] 5.2 Test business usage detection with BI job runs (verify access metrics updated)
- [x] 5.3 Test "live data" endpoint returns datasets with business usage
- [x] 5.4 Test "dead data" endpoint returns datasets without business usage
- [x] 5.5 Test business-critical paths are correctly identified
- [x] 5.6 Validate acceptance criteria: system can distinguish "live data" from "dead data"


