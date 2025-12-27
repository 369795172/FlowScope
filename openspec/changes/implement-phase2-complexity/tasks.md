## 1. Complexity Scoring Module

- [x] 1.1 Implement path complexity calculator (hop count, node count)
- [x] 1.2 Implement fan-in/fan-out ratio calculation for nodes in paths
- [x] 1.3 Implement transform density calculation (jobs per dataset in path)
- [x] 1.4 Create complexity scoring service (`flowspec/complexity/complexity_scorer.py`)
- [x] 1.5 Add complexity metrics to path query responses (enhance PathFinder or create wrapper)

## 2. Redundancy Detection Module

- [x] 2.1 Implement orphan dataset detector (no upstream AND no downstream connections)
- [x] 2.2 Implement duplicate table candidate identifier (name similarity + path overlap)
- [x] 2.3 Create redundancy detection service (`flowspec/redundancy/redundancy_detector.py`)
- [x] 2.4 Add similarity scoring algorithm for duplicate detection

## 3. API Endpoints

- [x] 3.1 Create complexity scoring endpoint (`GET /api/v1/datasets/{namespace}/{name}/complexity`)
- [x] 3.2 Create orphan detection endpoint (`GET /api/v1/redundancy/orphans`)
- [x] 3.3 Create duplicate detection endpoint (`GET /api/v1/redundancy/duplicates`)
- [x] 3.4 Enhance path query endpoints to include complexity scores in responses
- [x] 3.5 Add OpenAPI documentation for new endpoints

## 4. Testing and Validation

- [x] 4.1 Test complexity scoring with known lineage chains (verify metrics are correct)
- [x] 4.2 Test orphan detection with isolated datasets (verify orphans are identified)
- [x] 4.3 Test duplicate detection with similar tables (verify duplicates are identified)
- [x] 4.4 Test API endpoints return correct complexity and redundancy data
- [x] 4.5 Validate acceptance criteria: system provides "deletable/mergeable" candidate list

